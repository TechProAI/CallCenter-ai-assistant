"""
Test configuration and fixtures for CallSense.
"""

import pytest
import os
from unittest.mock import MagicMock, AsyncMock, patch

# Set test environment variables before importing app modules
os.environ["OPENAI_API_KEY"] = "test-key-123"
os.environ["SUPABASE_URL"] = "https://test.supabase.co"
os.environ["SUPABASE_KEY"] = "test-supabase-key"
os.environ["APP_ENV"] = "testing"

from fastapi.testclient import TestClient
from app.main import app


@pytest.fixture
def client():
    """FastAPI test client."""
    return TestClient(app)


@pytest.fixture
def sample_transcript():
    """Sample call transcript for testing."""
    return """
Agent: Thank you for calling TechSupport, my name is Sarah. How can I help you today?

Customer: Hi Sarah, I've been having issues with my internet connection for the past three days. It keeps dropping every few hours and it's really frustrating because I work from home.

Agent: I'm sorry to hear that. I understand how frustrating that must be, especially when you're working from home. Let me pull up your account and take a look. Can I have your account number please?

Customer: Sure, it's 4478932.

Agent: Thank you. I can see your account here. Let me check if there are any known outages in your area.

Customer: Yes, I've restarted it multiple times. Nothing works.

Agent: I appreciate you trying those steps already. I'm going to reset your connection from our end, which should resolve the intermittent drops.

Customer: Okay, I hope this works.

Agent: I've completed the reset. You should notice improved stability within the next hour. If the issue persists beyond 24 hours, please call us back and we can schedule a technician visit at no charge.

Customer: That sounds good. Thank you Sarah.

Agent: You're welcome! Have a great day.
"""


@pytest.fixture
def sample_summary_response():
    """Mock LLM response for summarization."""
    return {
        "brief_summary": "Customer called about internet connectivity issues lasting 3 days. Agent performed a remote connection reset.",
        "detailed_summary": "A customer contacted support regarding recurring internet drops over 3 days that impacted their remote work. The agent verified the account, ran diagnostics, and performed a connection reset.",
        "key_points": ["Internet dropping every few hours", "Customer works from home", "Agent performed remote reset"],
        "customer_intent": "Resolve intermittent internet connection drops",
        "action_items": ["Monitor connection stability", "Schedule technician if issue persists"],
        "issues_raised": ["Internet connection dropping intermittently for 3 days"],
        "resolution_provided": "Agent performed a remote connection reset from their end",
        "follow_up_needed": True,
        "follow_up_details": "Customer should call back if issue persists beyond 24 hours for technician visit",
    }


@pytest.fixture
def sample_quality_response():
    """Mock LLM response for quality scoring."""
    return {
        "empathy_score": {"score": 8.5, "justification": "Agent showed empathy", "highlights": ["Acknowledged frustration"], "improvements": []},
        "professionalism_score": {"score": 9.0, "justification": "Very professional", "highlights": ["Proper greeting"], "improvements": []},
        "resolution_score": {"score": 7.5, "justification": "Issue addressed with reset", "highlights": ["Offered technician visit"], "improvements": ["Could have offered credit"]},
        "communication_score": {"score": 8.0, "justification": "Clear communication", "highlights": ["Explained steps"], "improvements": []},
        "compliance_score": {"score": 8.5, "justification": "Followed protocols", "highlights": ["Proper greeting and closing"], "improvements": []},
        "active_listening_score": {"score": 7.0, "justification": "Good listening", "highlights": ["Acknowledged restart attempts"], "improvements": ["Could ask more about the issue"]},
        "overall_score": 8.1,
        "grade": "A",
        "overall_feedback": "Strong performance overall with good empathy and professionalism.",
    }


@pytest.fixture
def sample_sentiment_response():
    """Mock LLM response for sentiment analysis."""
    return {
        "overall_sentiment": "positive",
        "overall_confidence": 0.82,
        "customer_sentiment": "neutral",
        "agent_sentiment": "positive",
        "sentiment_trajectory": "improved",
        "phases": [
            {"phase": "opening", "sentiment": "neutral", "confidence": 0.8, "key_phrases": ["having issues"]},
            {"phase": "resolution", "sentiment": "positive", "confidence": 0.85, "key_phrases": ["sounds good"]},
        ],
        "emotional_triggers": ["Internet issues affecting work from home"],
    }


@pytest.fixture
def sample_routing_response():
    """Mock LLM response for routing."""
    return {
        "category": "technical_support",
        "urgency": "medium",
        "resolution_status": "resolved",
        "requires_escalation": False,
        "escalation_reason": None,
        "recommended_department": None,
        "tags": ["internet", "connectivity", "remote-work"],
        "priority_score": 5,
    }


@pytest.fixture
def sample_coaching_response():
    """Mock LLM response for coaching."""
    return {
        "strengths": ["Good empathy and acknowledgment", "Professional greeting and closing"],
        "areas_for_improvement": ["Could offer a service credit for the inconvenience"],
        "training_suggestions": ["Advanced troubleshooting techniques"],
        "example_responses": ["I understand how disruptive this must be for your work."],
        "overall_recommendation": "Strong performance. Focus on proactive resolution offers.",
    }
