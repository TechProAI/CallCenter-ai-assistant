"""
Coaching Recommendation Agent — generates actionable coaching feedback.
Creative addition: provides training suggestions and example improved responses.
"""

import logging
import json

from app.models.schemas import CoachingRecommendation, QualityScores, SentimentAnalysis
from app.services.openai_service import get_openai_service
from app.utils.prompts import COACHING_PROMPT

logger = logging.getLogger(__name__)


class CoachingAgent:
    """Generates coaching recommendations for call center agents."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def recommend(
        self,
        transcript: str,
        call_id: str,
        quality_scores: QualityScores = None,
        sentiment: SentimentAnalysis = None,
    ) -> CoachingRecommendation:
        """Generate coaching recommendations based on call analysis."""
        logger.info(f"[{call_id}] Generating coaching recommendations...")

        # Build context
        scores_text = ""
        if quality_scores:
            scores_text = json.dumps({
                "overall_score": quality_scores.overall_score,
                "grade": quality_scores.grade,
                "empathy": {
                    "score": quality_scores.empathy_score.score,
                    "improvements": quality_scores.empathy_score.improvements,
                },
                "professionalism": {
                    "score": quality_scores.professionalism_score.score,
                    "improvements": quality_scores.professionalism_score.improvements,
                },
                "resolution": {
                    "score": quality_scores.resolution_score.score,
                    "improvements": quality_scores.resolution_score.improvements,
                },
                "communication": {
                    "score": quality_scores.communication_score.score,
                    "improvements": quality_scores.communication_score.improvements,
                },
                "active_listening": {
                    "score": quality_scores.active_listening_score.score,
                    "improvements": quality_scores.active_listening_score.improvements,
                },
            })

        sentiment_text = ""
        if sentiment:
            sentiment_text = json.dumps({
                "overall_sentiment": sentiment.overall_sentiment.value,
                "customer_sentiment": sentiment.customer_sentiment.value,
                "trajectory": sentiment.sentiment_trajectory,
                "emotional_triggers": sentiment.emotional_triggers,
            })

        prompt = COACHING_PROMPT.format(
            transcript=transcript,
            quality_scores=scores_text or "Not available",
            sentiment=sentiment_text or "Not available",
        )

        result = self.openai_service.get_json_completion(
            prompt=prompt,
            system_message="You are a senior call center coach. Provide constructive, actionable coaching feedback.",
            max_tokens=2048,
        )

        coaching = CoachingRecommendation(
            call_id=call_id,
            strengths=result.get("strengths", []),
            areas_for_improvement=result.get("areas_for_improvement", []),
            training_suggestions=result.get("training_suggestions", []),
            example_responses=result.get("example_responses", []),
            overall_recommendation=result.get("overall_recommendation", ""),
        )

        logger.info(
            f"[{call_id}] Coaching: {len(coaching.strengths)} strengths, "
            f"{len(coaching.areas_for_improvement)} improvement areas"
        )
        return coaching
