"""
Routing Agent — categorizes calls, determines urgency, and makes routing decisions.
Uses context from previous agents (summary, quality scores) for informed decisions.
"""

import logging
import json

from app.models.schemas import (
    RoutingDecision, CallCategory, UrgencyLevel, ResolutionStatus,
    CallSummary, QualityScores,
)
from app.services.openai_service import get_openai_service
from app.utils.prompts import ROUTING_PROMPT

logger = logging.getLogger(__name__)

VALID_CATEGORIES = {c.value for c in CallCategory}
VALID_URGENCIES = {u.value for u in UrgencyLevel}
VALID_RESOLUTIONS = {r.value for r in ResolutionStatus}


class RoutingAgent:
    """Categorizes and routes calls based on analysis context."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def route(
        self,
        transcript: str,
        call_id: str,
        summary: CallSummary = None,
        quality_scores: QualityScores = None,
    ) -> RoutingDecision:
        """Determine routing, category, urgency, and resolution status."""
        logger.info(f"[{call_id}] Making routing decision...")

        # Build context from previous agents
        summary_text = ""
        if summary:
            summary_text = json.dumps({
                "brief_summary": summary.brief_summary,
                "customer_intent": summary.customer_intent,
                "issues_raised": summary.issues_raised,
                "follow_up_needed": summary.follow_up_needed,
            })

        quality_text = ""
        if quality_scores:
            quality_text = json.dumps({
                "overall_score": quality_scores.overall_score,
                "grade": quality_scores.grade,
                "resolution_score": quality_scores.resolution_score.score,
            })

        prompt = ROUTING_PROMPT.format(
            transcript=transcript,
            summary=summary_text or "Not available",
            quality_score=quality_text or "Not available",
        )

        result = self.openai_service.get_json_completion(
            prompt=prompt,
            system_message="You are a call center routing specialist. Make precise categorization and routing decisions.",
            max_tokens=1500,
        )

        # Validate enum values
        category = result.get("category", "other")
        category = category if category in VALID_CATEGORIES else "other"

        urgency = result.get("urgency", "medium")
        urgency = urgency if urgency in VALID_URGENCIES else "medium"

        resolution = result.get("resolution_status", "unresolved")
        resolution = resolution if resolution in VALID_RESOLUTIONS else "unresolved"

        routing = RoutingDecision(
            call_id=call_id,
            category=CallCategory(category),
            urgency=UrgencyLevel(urgency),
            resolution_status=ResolutionStatus(resolution),
            requires_escalation=result.get("requires_escalation", False),
            escalation_reason=result.get("escalation_reason"),
            recommended_department=result.get("recommended_department"),
            tags=result.get("tags", []),
            priority_score=min(max(int(result.get("priority_score", 5)), 1), 10),
        )

        logger.info(
            f"[{call_id}] Routing: category={category}, urgency={urgency}, "
            f"resolution={resolution}, escalation={routing.requires_escalation}"
        )
        return routing
