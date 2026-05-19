"""Tests for agents and utility functions."""

import pytest
from unittest.mock import patch, MagicMock

from app.utils.helpers import (
    generate_call_id, parse_llm_json, calculate_overall_quality_score,
    score_to_grade, validate_audio_format, truncate_text, format_file_size,
)
from app.models.schemas import CallStatus, CallCategory, SentimentLabel, UrgencyLevel


# ── Helper Tests ──

class TestHelpers:

    def test_generate_call_id(self):
        cid = generate_call_id()
        assert cid.startswith("call_")
        assert len(cid) == 17  # "call_" + 12 hex chars

    def test_generate_call_id_unique(self):
        ids = {generate_call_id() for _ in range(100)}
        assert len(ids) == 100

    def test_parse_llm_json_clean(self):
        result = parse_llm_json('{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_llm_json_with_markdown(self):
        result = parse_llm_json('```json\n{"key": "value"}\n```')
        assert result == {"key": "value"}

    def test_parse_llm_json_with_preamble(self):
        result = parse_llm_json('Here is the result:\n{"key": "value"}')
        assert result == {"key": "value"}

    def test_parse_llm_json_empty(self):
        with pytest.raises(ValueError):
            parse_llm_json("")

    def test_parse_llm_json_invalid(self):
        with pytest.raises(ValueError):
            parse_llm_json("not json at all")

    def test_calculate_overall_quality_score(self):
        scores = {
            "empathy_score": {"score": 8.0},
            "professionalism_score": {"score": 9.0},
            "resolution_score": {"score": 7.0},
            "communication_score": {"score": 8.0},
            "compliance_score": {"score": 8.5},
            "active_listening_score": {"score": 7.5},
        }
        result = calculate_overall_quality_score(scores)
        assert 7.0 <= result <= 9.0
        assert isinstance(result, float)

    def test_score_to_grade(self):
        assert score_to_grade(9.0) == "A"
        assert score_to_grade(8.0) == "A"
        assert score_to_grade(7.0) == "B"
        assert score_to_grade(5.0) == "C"
        assert score_to_grade(3.0) == "D"
        assert score_to_grade(1.0) == "F"

    def test_validate_audio_format_valid(self):
        assert validate_audio_format("test.wav", ["wav", "mp3"]) is True
        assert validate_audio_format("test.mp3", ["wav", "mp3"]) is True

    def test_validate_audio_format_invalid(self):
        assert validate_audio_format("test.exe", ["wav", "mp3"]) is False
        assert validate_audio_format("", ["wav", "mp3"]) is False

    def test_truncate_text(self):
        assert truncate_text("short", 10) == "short"
        assert truncate_text("a" * 600, 500).endswith("...")
        assert len(truncate_text("a" * 600, 500)) == 500

    def test_format_file_size(self):
        assert format_file_size(500) == "500 B"
        assert "KB" in format_file_size(5000)
        assert "MB" in format_file_size(5000000)


# ── Schema Tests ──

class TestSchemas:

    def test_call_status_values(self):
        assert CallStatus.COMPLETED == "completed"
        assert CallStatus.FAILED == "failed"
        assert CallStatus.PROCESSING == "processing"

    def test_call_category_values(self):
        assert CallCategory.BILLING == "billing"
        assert CallCategory.TECHNICAL_SUPPORT == "technical_support"

    def test_sentiment_label_values(self):
        assert SentimentLabel.POSITIVE == "positive"
        assert SentimentLabel.VERY_NEGATIVE == "very_negative"

    def test_urgency_level_values(self):
        assert UrgencyLevel.CRITICAL == "critical"
        assert UrgencyLevel.LOW == "low"


# ── Agent Tests (with mocked LLM) ──

class TestIntakeAgent:

    def test_process_transcript_valid(self, sample_transcript):
        from app.agents.intake_agent import IntakeAgent
        agent = IntakeAgent()
        result = agent.process_transcript(sample_transcript)
        assert result.is_valid is True
        assert result.input_type == "transcript"
        assert result.call_id.startswith("call_")

    def test_process_transcript_too_short(self):
        from app.agents.intake_agent import IntakeAgent
        agent = IntakeAgent()
        result = agent.process_transcript("too short")
        assert result.is_valid is False

    def test_process_transcript_too_long(self):
        from app.agents.intake_agent import IntakeAgent
        agent = IntakeAgent()
        result = agent.process_transcript("x" * 100001)
        assert result.is_valid is False


class TestSummarizationAgent:

    @patch("app.agents.summarization_agent.get_openai_service")
    def test_summarize(self, mock_openai, sample_transcript, sample_summary_response):
        mock_service = MagicMock()
        mock_service.get_json_completion.return_value = sample_summary_response
        mock_openai.return_value = mock_service

        from app.agents.summarization_agent import SummarizationAgent
        agent = SummarizationAgent()
        result = agent.summarize(sample_transcript, "test_123")

        assert result.call_id == "test_123"
        assert len(result.brief_summary) > 0
        assert len(result.key_points) > 0
        assert result.follow_up_needed is True


class TestQualityScoringAgent:

    @patch("app.agents.quality_scoring_agent.get_openai_service")
    def test_score(self, mock_openai, sample_transcript, sample_quality_response):
        mock_service = MagicMock()
        mock_service.get_json_completion.return_value = sample_quality_response
        mock_openai.return_value = mock_service

        from app.agents.quality_scoring_agent import QualityScoringAgent
        agent = QualityScoringAgent()
        result = agent.score(sample_transcript, "test_123")

        assert result.call_id == "test_123"
        assert 0 <= result.overall_score <= 10
        assert result.grade in ["A", "B", "C", "D", "F"]
        assert result.empathy_score.score >= 0


class TestSentimentAgent:

    @patch("app.agents.sentiment_agent.get_openai_service")
    def test_analyze(self, mock_openai, sample_transcript, sample_sentiment_response):
        mock_service = MagicMock()
        mock_service.get_json_completion.return_value = sample_sentiment_response
        mock_openai.return_value = mock_service

        from app.agents.sentiment_agent import SentimentAgent
        agent = SentimentAgent()
        result = agent.analyze(sample_transcript, "test_123")

        assert result.call_id == "test_123"
        assert result.overall_sentiment.value in ["very_positive", "positive", "neutral", "negative", "very_negative"]
        assert 0 <= result.overall_confidence <= 1


class TestRoutingAgent:

    @patch("app.agents.routing_agent.get_openai_service")
    def test_route(self, mock_openai, sample_transcript, sample_routing_response):
        mock_service = MagicMock()
        mock_service.get_json_completion.return_value = sample_routing_response
        mock_openai.return_value = mock_service

        from app.agents.routing_agent import RoutingAgent
        agent = RoutingAgent()
        result = agent.route(sample_transcript, "test_123")

        assert result.call_id == "test_123"
        assert result.category.value == "technical_support"
        assert 1 <= result.priority_score <= 10


class TestCoachingAgent:

    @patch("app.agents.coaching_agent.get_openai_service")
    def test_recommend(self, mock_openai, sample_transcript, sample_coaching_response):
        mock_service = MagicMock()
        mock_service.get_json_completion.return_value = sample_coaching_response
        mock_openai.return_value = mock_service

        from app.agents.coaching_agent import CoachingAgent
        agent = CoachingAgent()
        result = agent.recommend(sample_transcript, "test_123")

        assert result.call_id == "test_123"
        assert len(result.strengths) > 0
        assert len(result.overall_recommendation) > 0
