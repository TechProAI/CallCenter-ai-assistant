"""
Calls Router — handles call upload, analysis, and retrieval endpoints.
"""

import logging
from typing import Optional
from fastapi import APIRouter, UploadFile, File, Form, HTTPException, BackgroundTasks
from fastapi.responses import StreamingResponse
import io

from app.models.schemas import (
    TranscriptInput, CallListResponse, CallListItem, CallAnalysisResult,
    CallMetadata, CallStatus, AnalysisStatusResponse,
)
from app.agents.intake_agent import IntakeAgent
from app.agents.orchestrator import run_analysis
from app.services.supabase_service import get_supabase_service
from app.services.audio_service import get_audio_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/calls", tags=["Calls"])


@router.post("/upload-audio", response_model=AnalysisStatusResponse)
async def upload_audio(
    background_tasks: BackgroundTasks,
    file: UploadFile = File(...),
    language: str = Form(default="auto"),
):
    """
    Upload an audio file for analysis.
    The analysis runs in the background; poll /status/{call_id} for progress.
    """
    # Read file
    content = await file.read()
    filename = file.filename or "unknown.wav"

    # Intake validation
    intake_agent = IntakeAgent()
    intake_result = await intake_agent.process_audio(content, filename)

    if not intake_result.is_valid:
        raise HTTPException(status_code=400, detail=intake_result.validation_message)

    # Create call record in DB
    db = get_supabase_service()
    db.create_call({
        "call_id": intake_result.call_id,
        "status": CallStatus.PROCESSING,
        "input_type": "audio",
        "file_name": intake_result.metadata.file_name,
        "file_size_bytes": intake_result.metadata.file_size_bytes,
        "audio_format": intake_result.metadata.audio_format,
        "duration_seconds": intake_result.metadata.duration_seconds,
        "source": "upload",
    })

    # Get the saved file path
    audio_service = get_audio_service()
    file_path, _ = await audio_service.save_upload(content, filename)

    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        call_id=intake_result.call_id,
        input_type="audio",
        audio_file_path=file_path,
    )

    return AnalysisStatusResponse(
        call_id=intake_result.call_id,
        status=CallStatus.PROCESSING,
        message="Audio uploaded. Analysis started in background.",
        progress_percent=10,
    )


@router.post("/analyze-transcript", response_model=AnalysisStatusResponse)
async def analyze_transcript(
    background_tasks: BackgroundTasks,
    body: TranscriptInput,
):
    """
    Submit a text transcript for analysis.
    The analysis runs in the background.
    """
    intake_agent = IntakeAgent()
    intake_result = intake_agent.process_transcript(
        transcript=body.transcript,
        caller_name=body.caller_name,
        agent_name=body.agent_name,
        call_date=body.call_date,
    )

    if not intake_result.is_valid:
        raise HTTPException(status_code=400, detail=intake_result.validation_message)

    # Create call record
    db = get_supabase_service()
    db.create_call({
        "call_id": intake_result.call_id,
        "status": CallStatus.PROCESSING,
        "input_type": "transcript",
        "source": "transcript_paste",
        "caller_name": body.caller_name,
        "agent_name": body.agent_name,
        "call_date": body.call_date,
    })

    # Run analysis in background
    background_tasks.add_task(
        run_analysis,
        call_id=intake_result.call_id,
        input_type="transcript",
        raw_transcript=body.transcript,
        caller_name=body.caller_name,
        agent_name=body.agent_name,
        call_date=body.call_date,
    )

    return AnalysisStatusResponse(
        call_id=intake_result.call_id,
        status=CallStatus.PROCESSING,
        message="Transcript received. Analysis started in background.",
        progress_percent=10,
    )


@router.get("/status/{call_id}", response_model=AnalysisStatusResponse)
async def get_analysis_status(call_id: str):
    """Check the status of a call analysis."""
    db = get_supabase_service()
    call = db.get_call(call_id)

    if not call:
        raise HTTPException(status_code=404, detail="Call not found")

    status = call.get("status", "unknown")
    progress_map = {
        "pending": 0,
        "processing": 10,
        "transcribing": 25,
        "summarizing": 45,
        "scoring": 60,
        "analyzing": 75,
        "completed": 100,
        "failed": 0,
    }

    messages = {
        "pending": "Call is queued for processing.",
        "processing": "Analysis pipeline starting...",
        "transcribing": "Transcribing audio...",
        "summarizing": "Generating summary...",
        "scoring": "Evaluating quality...",
        "analyzing": "Analyzing sentiment...",
        "completed": "Analysis complete.",
        "failed": f"Analysis failed: {call.get('error', 'Unknown error')}",
    }

    return AnalysisStatusResponse(
        call_id=call_id,
        status=CallStatus(status) if status in CallStatus.__members__.values() else CallStatus.PENDING,
        message=messages.get(status, "Processing..."),
        progress_percent=progress_map.get(status, 0),
    )


@router.get("/{call_id}", response_model=dict)
async def get_call_analysis(call_id: str):
    """Get the complete analysis for a call."""
    db = get_supabase_service()
    analysis = db.get_full_analysis(call_id)

    if not analysis or not analysis.get("call"):
        raise HTTPException(status_code=404, detail="Call not found")

    return analysis


@router.get("/{call_id}/transcript")
async def get_transcript(call_id: str):
    """Get the transcript for a call."""
    db = get_supabase_service()
    transcript = db.get_transcript(call_id)
    if not transcript:
        raise HTTPException(status_code=404, detail="Transcript not found")
    return transcript


@router.get("/{call_id}/summary")
async def get_summary(call_id: str):
    """Get the summary for a call."""
    db = get_supabase_service()
    summary = db.get_summary(call_id)
    if not summary:
        raise HTTPException(status_code=404, detail="Summary not found")
    return summary


@router.get("/{call_id}/scores")
async def get_quality_scores(call_id: str):
    """Get quality scores for a call."""
    db = get_supabase_service()
    scores = db.get_quality_scores(call_id)
    if not scores:
        raise HTTPException(status_code=404, detail="Quality scores not found")
    return scores


@router.get("/{call_id}/sentiment")
async def get_sentiment(call_id: str):
    """Get sentiment analysis for a call."""
    db = get_supabase_service()
    sentiment = db.get_sentiment(call_id)
    if not sentiment:
        raise HTTPException(status_code=404, detail="Sentiment analysis not found")
    return sentiment


@router.get("/{call_id}/routing")
async def get_routing(call_id: str):
    """Get routing decision for a call."""
    db = get_supabase_service()
    routing = db.get_routing(call_id)
    if not routing:
        raise HTTPException(status_code=404, detail="Routing decision not found")
    return routing


@router.get("/{call_id}/coaching")
async def get_coaching(call_id: str):
    """Get coaching recommendations for a call."""
    db = get_supabase_service()
    coaching = db.get_coaching(call_id)
    if not coaching:
        raise HTTPException(status_code=404, detail="Coaching recommendations not found")
    return coaching


@router.get("/", response_model=CallListResponse)
async def list_calls(page: int = 1, page_size: int = 20):
    """List all calls with pagination."""
    db = get_supabase_service()
    calls, total = db.list_calls(page, page_size)

    items = []
    for call in calls:
        items.append(CallListItem(
            call_id=call["call_id"],
            status=CallStatus(call.get("status", "pending")),
            category=call.get("category"),
            overall_score=None,
            overall_sentiment=None,
            brief_summary=None,
            urgency=None,
            resolution_status=None,
            created_at=call.get("created_at", ""),
            duration_seconds=call.get("duration_seconds"),
        ))

    return CallListResponse(
        calls=items,
        total_count=total,
        page=page,
        page_size=page_size,
    )


@router.delete("/{call_id}")
async def delete_call(call_id: str):
    """Delete a call and all related data."""
    db = get_supabase_service()
    success = db.delete_call(call_id)
    if not success:
        raise HTTPException(status_code=404, detail="Call not found")
    return {"message": "Call deleted successfully", "call_id": call_id}


@router.get("/{call_id}/export-pdf")
async def export_pdf(call_id: str):
    """Export call analysis as a PDF report."""
    from app.services.pdf_service import get_pdf_service

    db = get_supabase_service()
    analysis = db.get_full_analysis(call_id)

    if not analysis or not analysis.get("call"):
        raise HTTPException(status_code=404, detail="Call not found")

    if analysis["call"].get("status") != "completed":
        raise HTTPException(status_code=400, detail="Analysis not yet completed")

    pdf_service = get_pdf_service()
    pdf_bytes = pdf_service.generate_report(analysis)

    return StreamingResponse(
        io.BytesIO(pdf_bytes),
        media_type="application/pdf",
        headers={"Content-Disposition": f"attachment; filename=callsense_report_{call_id}.pdf"},
    )
