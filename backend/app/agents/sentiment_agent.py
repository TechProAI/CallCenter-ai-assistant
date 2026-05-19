"""
Sentiment Analysis Agent — analyzes emotional dynamics throughout the call.
Tracks sentiment phases, trajectory, and emotional triggers.
"""

import logging

from app.models.schemas import SentimentAnalysis, SentimentPhase, SentimentLabel
from app.services.openai_service import get_openai_service
from app.utils.prompts import SENTIMENT_ANALYSIS_PROMPT

logger = logging.getLogger(__name__)

VALID_SENTIMENTS = {s.value for s in SentimentLabel}


class SentimentAgent:
    """Analyzes sentiment dynamics in call transcripts."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def analyze(self, transcript: str, call_id: str) -> SentimentAnalysis:
        """Perform sentiment analysis on the call."""
        logger.info(f"[{call_id}] Analyzing sentiment...")

        prompt = SENTIMENT_ANALYSIS_PROMPT.format(transcript=transcript)

        result = self.openai_service.get_json_completion(
            prompt=prompt,
            system_message="You are a sentiment analysis expert specializing in customer service interactions.",
            max_tokens=2048,
        )

        # Parse phases
        phases = []
        for phase_data in result.get("phases", []):
            sentiment_val = phase_data.get("sentiment", "neutral")
            if sentiment_val not in VALID_SENTIMENTS:
                sentiment_val = "neutral"

            phases.append(
                SentimentPhase(
                    phase=phase_data.get("phase", "unknown"),
                    sentiment=SentimentLabel(sentiment_val),
                    confidence=min(max(float(phase_data.get("confidence", 0.5)), 0), 1),
                    key_phrases=phase_data.get("key_phrases", []),
                )
            )

        # Validate sentiment values
        overall = result.get("overall_sentiment", "neutral")
        customer = result.get("customer_sentiment", "neutral")
        agent = result.get("agent_sentiment", "neutral")

        overall = overall if overall in VALID_SENTIMENTS else "neutral"
        customer = customer if customer in VALID_SENTIMENTS else "neutral"
        agent = agent if agent in VALID_SENTIMENTS else "neutral"

        trajectory = result.get("sentiment_trajectory", "stable")
        valid_trajectories = {"improved", "declined", "stable", "mixed"}
        trajectory = trajectory if trajectory in valid_trajectories else "stable"

        analysis = SentimentAnalysis(
            call_id=call_id,
            overall_sentiment=SentimentLabel(overall),
            overall_confidence=min(max(float(result.get("overall_confidence", 0.5)), 0), 1),
            customer_sentiment=SentimentLabel(customer),
            agent_sentiment=SentimentLabel(agent),
            sentiment_trajectory=trajectory,
            phases=phases,
            emotional_triggers=result.get("emotional_triggers", []),
        )

        logger.info(
            f"[{call_id}] Sentiment: {overall} (trajectory: {trajectory}), "
            f"{len(phases)} phases analyzed"
        )
        return analysis
