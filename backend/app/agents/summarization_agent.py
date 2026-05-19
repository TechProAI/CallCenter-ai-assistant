"""
Summarization Agent — generates structured call summaries.
Extracts key points, action items, issues, and resolution details.
"""

import logging

from app.models.schemas import CallSummary
from app.services.openai_service import get_openai_service
from app.utils.prompts import SUMMARIZATION_PROMPT

logger = logging.getLogger(__name__)


class SummarizationAgent:
    """Generates structured summaries from call transcripts."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def summarize(self, transcript: str, call_id: str) -> CallSummary:
        """Generate a structured summary of the call."""
        logger.info(f"[{call_id}] Generating summary...")

        prompt = SUMMARIZATION_PROMPT.format(transcript=transcript)

        result = self.openai_service.get_json_completion(
            prompt=prompt,
            system_message="You are an expert call center analyst who produces precise, structured summaries.",
            max_tokens=2048,
        )

        summary = CallSummary(
            call_id=call_id,
            brief_summary=result.get("brief_summary", ""),
            detailed_summary=result.get("detailed_summary", ""),
            key_points=result.get("key_points", []),
            customer_intent=result.get("customer_intent", ""),
            action_items=result.get("action_items", []),
            issues_raised=result.get("issues_raised", []),
            resolution_provided=result.get("resolution_provided", ""),
            follow_up_needed=result.get("follow_up_needed", False),
            follow_up_details=result.get("follow_up_details"),
        )

        logger.info(
            f"[{call_id}] Summary generated: {len(summary.key_points)} key points, "
            f"{len(summary.action_items)} action items"
        )
        return summary
