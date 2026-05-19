"""
LangGraph Orchestrator — coordinates the multi-agent pipeline.
Manages state, conditional routing, fallback logic, and agent execution.

OPTIMIZED Pipeline (parallel execution):
  Transcription → [Summarization ∥ Quality Scoring ∥ Sentiment] → [Routing ∥ Coaching] → Finalize

Sequential (~60s) vs Parallel (~30-35s) — nearly 2x faster.
"""

import time
import logging
from typing import TypedDict, Optional, Any
from concurrent.futures import ThreadPoolExecutor, as_completed
from langgraph.graph import StateGraph, END

from app.models.schemas import (
    CallStatus, CallIntakeResult, TranscriptionResult, CallSummary,
    QualityScores, SentimentAnalysis, RoutingDecision, CoachingRecommendation,
    CallAnalysisResult, CallMetadata,
)
from app.agents.intake_agent import IntakeAgent
from app.agents.transcription_agent import TranscriptionAgent
from app.agents.summarization_agent import SummarizationAgent
from app.agents.quality_scoring_agent import QualityScoringAgent
from app.agents.sentiment_agent import SentimentAgent
from app.agents.routing_agent import RoutingAgent
from app.agents.coaching_agent import CoachingAgent
from app.services.supabase_service import get_supabase_service
from app.services.audio_service import get_audio_service

logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# State Definition
# ──────────────────────────────────────────────

class PipelineState(TypedDict):
    """State passed between agents in the pipeline."""
    # Input
    call_id: str
    input_type: str  # "audio" or "transcript"
    audio_file_path: Optional[str]
    raw_transcript: Optional[str]
    caller_name: Optional[str]
    agent_name: Optional[str]
    call_date: Optional[str]

    # Intake
    intake_result: Optional[dict]

    # Agent outputs
    transcript: Optional[dict]
    summary: Optional[dict]
    quality_scores: Optional[dict]
    sentiment: Optional[dict]
    routing: Optional[dict]
    coaching: Optional[dict]

    # Pipeline control
    status: str
    error: Optional[str]
    start_time: float


# ──────────────────────────────────────────────
# Node Functions
# ──────────────────────────────────────────────

def transcription_node(state: PipelineState) -> dict:
    """Transcribe audio or process provided transcript."""
    call_id = state["call_id"]
    try:
        db = get_supabase_service()
        db.update_call_status(call_id, CallStatus.TRANSCRIBING)

        agent = TranscriptionAgent()

        if state["input_type"] == "audio" and state.get("audio_file_path"):
            result = agent.transcribe_audio(state["audio_file_path"], call_id)  # Convert audio to text
            # Cleanup audio file after transcription
            audio_service = get_audio_service()
            audio_service.cleanup(state["audio_file_path"])  # Delete file after use
        elif state.get("raw_transcript"):
            result = agent.process_transcript(state["raw_transcript"], call_id)
        else:
            raise ValueError("No audio file or transcript provided")

        # Save to DB
        db.save_transcript(call_id, {
            "full_text": result.full_text,
            "segments": [s.model_dump() for s in result.segments],
            "language": result.language,
            "confidence": result.confidence,
            "duration_seconds": result.duration_seconds,
        })

        return {"transcript": result.model_dump(), "status": "transcribed"}

    except Exception as e:
        logger.error(f"[{call_id}] Transcription failed: {e}")
        return {"error": f"Transcription failed: {str(e)}", "status": "failed"}


def _run_summarization(call_id: str, transcript_text: str) -> dict:
    """Run summarization agent (for parallel execution)."""
    try:
        agent = SummarizationAgent()
        result = agent.summarize(transcript_text, call_id)

        db = get_supabase_service()
        db.save_summary(call_id, {
            "brief_summary": result.brief_summary,
            "detailed_summary": result.detailed_summary,
            "key_points": result.key_points,
            "customer_intent": result.customer_intent,
            "action_items": result.action_items,
            "issues_raised": result.issues_raised,
            "resolution_provided": result.resolution_provided,
            "follow_up_needed": result.follow_up_needed,
            "follow_up_details": result.follow_up_details,
        })
        return {"summary": result.model_dump()}
    except Exception as e:
        logger.error(f"[{call_id}] Summarization failed: {e}")
        return {"summary": None}


def _run_quality_scoring(call_id: str, transcript_text: str) -> dict:
    """Run quality scoring agent (for parallel execution)."""
    try:
        agent = QualityScoringAgent()
        result = agent.score(transcript_text, call_id)

        db = get_supabase_service()
        db.save_quality_scores(call_id, {
            "empathy_score": result.empathy_score.model_dump(),
            "professionalism_score": result.professionalism_score.model_dump(),
            "resolution_score": result.resolution_score.model_dump(),
            "communication_score": result.communication_score.model_dump(),
            "compliance_score": result.compliance_score.model_dump(),
            "active_listening_score": result.active_listening_score.model_dump(),
            "overall_score": result.overall_score,
            "grade": result.grade,
            "overall_feedback": result.overall_feedback,
        })
        return {"quality_scores": result.model_dump()}
    except Exception as e:
        logger.error(f"[{call_id}] Quality scoring failed: {e}")
        return {"quality_scores": None}


def _run_sentiment(call_id: str, transcript_text: str) -> dict:
    """Run sentiment analysis agent (for parallel execution)."""
    try:
        agent = SentimentAgent()
        result = agent.analyze(transcript_text, call_id)

        db = get_supabase_service()
        db.save_sentiment(call_id, {
            "overall_sentiment": result.overall_sentiment.value,
            "overall_confidence": result.overall_confidence,
            "customer_sentiment": result.customer_sentiment.value,
            "agent_sentiment": result.agent_sentiment.value,
            "sentiment_trajectory": result.sentiment_trajectory,
            "phases": [p.model_dump() for p in result.phases],
            "emotional_triggers": result.emotional_triggers,
        })
        return {"sentiment": result.model_dump()}
    except Exception as e:
        logger.error(f"[{call_id}] Sentiment analysis failed: {e}")
        return {"sentiment": None}


def _run_routing(call_id: str, transcript_text: str, summary: dict, quality_scores: dict) -> dict:
    """Run routing agent (for parallel execution)."""
    try:
        agent = RoutingAgent()

        summary_obj = CallSummary(**summary) if summary else None
        scores_obj = QualityScores(**quality_scores) if quality_scores else None

        result = agent.route(transcript_text, call_id, summary_obj, scores_obj)

        db = get_supabase_service()
        db.save_routing(call_id, {
            "category": result.category.value,
            "urgency": result.urgency.value,
            "resolution_status": result.resolution_status.value,
            "requires_escalation": result.requires_escalation,
            "escalation_reason": result.escalation_reason,
            "recommended_department": result.recommended_department,
            "tags": result.tags,
            "priority_score": result.priority_score,
        })
        return {"routing": result.model_dump()}
    except Exception as e:
        logger.error(f"[{call_id}] Routing failed: {e}")
        return {"routing": None}


def _run_coaching(call_id: str, transcript_text: str, quality_scores: dict, sentiment: dict) -> dict:
    """Run coaching agent (for parallel execution)."""
    try:
        agent = CoachingAgent()

        scores_obj = QualityScores(**quality_scores) if quality_scores else None
        sentiment_obj = SentimentAnalysis(**sentiment) if sentiment else None

        result = agent.recommend(transcript_text, call_id, scores_obj, sentiment_obj)

        db = get_supabase_service()
        db.save_coaching(call_id, {
            "strengths": result.strengths,
            "areas_for_improvement": result.areas_for_improvement,
            "training_suggestions": result.training_suggestions,
            "example_responses": result.example_responses,
            "overall_recommendation": result.overall_recommendation,
        })
        return {"coaching": result.model_dump()}
    except Exception as e:
        logger.error(f"[{call_id}] Coaching failed: {e}")
        return {"coaching": None}


def parallel_analysis_node(state: PipelineState) -> dict:
    """
    Run Summarization + Quality Scoring + Sentiment in PARALLEL.
    These three agents only need the transcript — no dependencies on each other.
    Saves ~20 seconds compared to sequential execution.
    """
    call_id = state["call_id"]
    transcript_text = state["transcript"]["full_text"]

    db = get_supabase_service()
    db.update_call_status(call_id, CallStatus.SUMMARIZING)

    logger.info(f"[{call_id}] Starting parallel analysis (summarize + score + sentiment)...")
    start = time.time()

    results = {}

    with ThreadPoolExecutor(max_workers=3) as executor:
        futures = {
            executor.submit(_run_summarization, call_id, transcript_text): "summary",
            executor.submit(_run_quality_scoring, call_id, transcript_text): "quality_scores",
            executor.submit(_run_sentiment, call_id, transcript_text): "sentiment",
        }

        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                result = future.result()
                results.update(result)
                logger.info(f"[{call_id}] {agent_name} completed")
            except Exception as e:
                logger.error(f"[{call_id}] {agent_name} failed in parallel: {e}")
                results[agent_name] = None

    elapsed = round(time.time() - start, 2)
    logger.info(f"[{call_id}] Parallel analysis done in {elapsed}s")

    return results


def parallel_post_analysis_node(state: PipelineState) -> dict:
    """
    Run Routing + Coaching in PARALLEL.
    Both need results from the previous stage but don't depend on each other.
    Saves ~8 seconds compared to sequential execution.
    """
    call_id = state["call_id"]
    transcript_text = state["transcript"]["full_text"]

    db = get_supabase_service()
    db.update_call_status(call_id, CallStatus.ANALYZING)

    logger.info(f"[{call_id}] Starting parallel post-analysis (route + coach)...")
    start = time.time()

    results = {}

    with ThreadPoolExecutor(max_workers=2) as executor:
        futures = {
            executor.submit(
                _run_routing, call_id, transcript_text,
                state.get("summary"), state.get("quality_scores")
            ): "routing",
            executor.submit(
                _run_coaching, call_id, transcript_text,
                state.get("quality_scores"), state.get("sentiment")
            ): "coaching",
        }

        for future in as_completed(futures):
            agent_name = futures[future]
            try:
                result = future.result()
                results.update(result)
                logger.info(f"[{call_id}] {agent_name} completed")
            except Exception as e:
                logger.error(f"[{call_id}] {agent_name} failed in parallel: {e}")
                results[agent_name] = None

    elapsed = round(time.time() - start, 2)
    logger.info(f"[{call_id}] Parallel post-analysis done in {elapsed}s")

    return results


def finalize_node(state: PipelineState) -> dict:
    """Finalize the pipeline and update status."""
    call_id = state["call_id"]
    processing_time = round(time.time() - state["start_time"], 2)

    db = get_supabase_service()

    if state.get("error") and state.get("status") == "failed":
        db.update_call_status(call_id, CallStatus.FAILED, error=state["error"],
                              processing_time=processing_time)
    else:
        db.update_call_status(call_id, CallStatus.COMPLETED,
                              processing_time=processing_time)

    logger.info(f"[{call_id}] Pipeline complete in {processing_time}s")
    return {"status": "completed"}


# ──────────────────────────────────────────────
# Conditional Edges
# ──────────────────────────────────────────────

def should_continue_after_transcription(state: PipelineState) -> str:
    """Check if transcription succeeded before continuing."""
    if state.get("status") == "failed" or not state.get("transcript"):
        return "finalize"
    return "analyze"


# ──────────────────────────────────────────────
# Build the Graph
# ──────────────────────────────────────────────

def build_pipeline() -> StateGraph:
    """
    Build the OPTIMIZED LangGraph pipeline.

    Flow:
      Transcribe → [Summarize ∥ Score ∥ Sentiment] → [Route ∥ Coach] → Finalize

    Stage 1: Transcription (sequential — must complete first)
    Stage 2: Parallel analysis — 3 agents run simultaneously
    Stage 3: Parallel post-analysis — 2 agents run simultaneously
    Stage 4: Finalize
    """

    workflow = StateGraph(PipelineState)

    # Add nodes (only 4 nodes now — parallel work happens inside nodes)
    workflow.add_node("transcribe", transcription_node)
    workflow.add_node("parallel_analysis", parallel_analysis_node)
    workflow.add_node("parallel_post_analysis", parallel_post_analysis_node)
    workflow.add_node("finalize", finalize_node)

    # Set entry point
    workflow.set_entry_point("transcribe")

    # Conditional edge after transcription
    workflow.add_conditional_edges(
        "transcribe",
        should_continue_after_transcription,
        {
            "analyze": "parallel_analysis",
            "finalize": "finalize",
        },
    )

    # Parallel analysis → Parallel post-analysis → Finalize
    workflow.add_edge("parallel_analysis", "parallel_post_analysis")
    workflow.add_edge("parallel_post_analysis", "finalize")
    workflow.add_edge("finalize", END)

    return workflow.compile()


# ──────────────────────────────────────────────
# Public API
# ──────────────────────────────────────────────

# Compiled pipeline (singleton)
_pipeline = None


def get_pipeline():
    """Get or create the compiled pipeline."""
    global _pipeline
    if _pipeline is None:
        _pipeline = build_pipeline()
    return _pipeline


async def run_analysis(
    call_id: str,
    input_type: str,
    audio_file_path: Optional[str] = None,
    raw_transcript: Optional[str] = None,
    caller_name: Optional[str] = None,
    agent_name: Optional[str] = None,
    call_date: Optional[str] = None,
) -> dict:
    """
    Run the full analysis pipeline for a call.
    Returns the final state.
    """
    pipeline = get_pipeline()

    initial_state: PipelineState = {
        "call_id": call_id,
        "input_type": input_type,
        "audio_file_path": audio_file_path,
        "raw_transcript": raw_transcript,
        "caller_name": caller_name,
        "agent_name": agent_name,
        "call_date": call_date,
        "intake_result": None,
        "transcript": None,
        "summary": None,
        "quality_scores": None,
        "sentiment": None,
        "routing": None,
        "coaching": None,
        "status": "processing",
        "error": None,
        "start_time": time.time(),
    }

    logger.info(f"[{call_id}] Starting OPTIMIZED pipeline (type={input_type})...")

    # Run the pipeline
    final_state = pipeline.invoke(initial_state)

    logger.info(f"[{call_id}] Pipeline finished with status: {final_state.get('status')}")
    return final_state