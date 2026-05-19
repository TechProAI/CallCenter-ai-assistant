"""
Quality Scoring Agent — evaluates call quality across multiple dimensions.
Scores empathy, professionalism, resolution, communication, compliance, and active listening.
"""

import logging

from app.models.schemas import QualityScores, ScoreBreakdown
from app.services.openai_service import get_openai_service
from app.utils.prompts import QUALITY_SCORING_PROMPT
from app.utils.helpers import calculate_overall_quality_score, score_to_grade

logger = logging.getLogger(__name__)


class QualityScoringAgent:
    """Evaluates call quality and produces detailed scores with justification."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def score(self, transcript: str, call_id: str) -> QualityScores:
        """Score the call across all quality dimensions."""
        logger.info(f"[{call_id}] Scoring call quality...")

        prompt = QUALITY_SCORING_PROMPT.format(transcript=transcript)

        result = self.openai_service.get_json_completion(
            prompt=prompt,
            system_message="You are a senior QA evaluator. Score fairly and provide specific evidence for each score.",
            max_tokens=3000,
        )

        # Build score breakdowns
        def build_breakdown(data: dict) -> ScoreBreakdown:
            return ScoreBreakdown(
                score=min(max(float(data.get("score", 5)), 0), 10),
                justification=data.get("justification", "No justification provided."),
                highlights=data.get("highlights", []),
                improvements=data.get("improvements", []),
            )

        empathy = build_breakdown(result.get("empathy_score", {}))
        professionalism = build_breakdown(result.get("professionalism_score", {}))
        resolution = build_breakdown(result.get("resolution_score", {}))
        communication = build_breakdown(result.get("communication_score", {}))
        compliance = build_breakdown(result.get("compliance_score", {}))
        active_listening = build_breakdown(result.get("active_listening_score", {}))

        # Calculate overall score using weights
        overall = calculate_overall_quality_score({
            "empathy_score": {"score": empathy.score},
            "professionalism_score": {"score": professionalism.score},
            "resolution_score": {"score": resolution.score},
            "communication_score": {"score": communication.score},
            "compliance_score": {"score": compliance.score},
            "active_listening_score": {"score": active_listening.score},
        })

        grade = score_to_grade(overall)

        scores = QualityScores(
            call_id=call_id,
            empathy_score=empathy,
            professionalism_score=professionalism,
            resolution_score=resolution,
            communication_score=communication,
            compliance_score=compliance,
            active_listening_score=active_listening,
            overall_score=overall,
            grade=grade,
            overall_feedback=result.get("overall_feedback", ""),
        )

        logger.info(f"[{call_id}] Quality score: {overall}/10 (Grade: {grade})")
        return scores
