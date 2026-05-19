"""
Supabase service for database operations.
Handles all CRUD operations for calls, transcripts, summaries, scores, etc.
"""

import logging
from typing import Optional, List, Dict, Any
from supabase import create_client, Client

from app.config import get_settings
from app.utils.helpers import get_utc_now

logger = logging.getLogger(__name__)

# ──────────────────────────────────────────────
# SQL for creating tables (run in Supabase SQL editor)
# ──────────────────────────────────────────────
SETUP_SQL = """
-- Calls table: stores call metadata and status
CREATE TABLE IF NOT EXISTS calls (
    call_id TEXT PRIMARY KEY,
    status TEXT NOT NULL DEFAULT 'pending',
    input_type TEXT NOT NULL DEFAULT 'audio',
    file_name TEXT,
    file_size_bytes BIGINT,
    audio_format TEXT,
    duration_seconds FLOAT,
    source TEXT DEFAULT 'upload',
    caller_name TEXT,
    agent_name TEXT,
    call_date TEXT,
    error TEXT,
    processing_time_seconds FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW(),
    updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Transcripts table
CREATE TABLE IF NOT EXISTS transcripts (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    full_text TEXT NOT NULL,
    segments JSONB DEFAULT '[]',
    language TEXT DEFAULT 'en',
    confidence FLOAT,
    duration_seconds FLOAT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Summaries table
CREATE TABLE IF NOT EXISTS summaries (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    brief_summary TEXT,
    detailed_summary TEXT,
    key_points JSONB DEFAULT '[]',
    customer_intent TEXT,
    action_items JSONB DEFAULT '[]',
    issues_raised JSONB DEFAULT '[]',
    resolution_provided TEXT,
    follow_up_needed BOOLEAN DEFAULT FALSE,
    follow_up_details TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Quality Scores table
CREATE TABLE IF NOT EXISTS quality_scores (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    empathy_score JSONB,
    professionalism_score JSONB,
    resolution_score JSONB,
    communication_score JSONB,
    compliance_score JSONB,
    active_listening_score JSONB,
    overall_score FLOAT,
    grade TEXT,
    overall_feedback TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Sentiment Analysis table
CREATE TABLE IF NOT EXISTS sentiments (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    overall_sentiment TEXT,
    overall_confidence FLOAT,
    customer_sentiment TEXT,
    agent_sentiment TEXT,
    sentiment_trajectory TEXT,
    phases JSONB DEFAULT '[]',
    emotional_triggers JSONB DEFAULT '[]',
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Routing Decisions table
CREATE TABLE IF NOT EXISTS routing_decisions (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    category TEXT,
    urgency TEXT,
    resolution_status TEXT,
    requires_escalation BOOLEAN DEFAULT FALSE,
    escalation_reason TEXT,
    recommended_department TEXT,
    tags JSONB DEFAULT '[]',
    priority_score INT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Coaching Recommendations table
CREATE TABLE IF NOT EXISTS coaching (
    id BIGSERIAL PRIMARY KEY,
    call_id TEXT REFERENCES calls(call_id) ON DELETE CASCADE,
    strengths JSONB DEFAULT '[]',
    areas_for_improvement JSONB DEFAULT '[]',
    training_suggestions JSONB DEFAULT '[]',
    example_responses JSONB DEFAULT '[]',
    overall_recommendation TEXT,
    created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Create indexes for common queries
CREATE INDEX IF NOT EXISTS idx_calls_status ON calls(status);
CREATE INDEX IF NOT EXISTS idx_calls_created_at ON calls(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_transcripts_call_id ON transcripts(call_id);
CREATE INDEX IF NOT EXISTS idx_summaries_call_id ON summaries(call_id);
CREATE INDEX IF NOT EXISTS idx_quality_scores_call_id ON quality_scores(call_id);
CREATE INDEX IF NOT EXISTS idx_sentiments_call_id ON sentiments(call_id);
CREATE INDEX IF NOT EXISTS idx_routing_call_id ON routing_decisions(call_id);
CREATE INDEX IF NOT EXISTS idx_coaching_call_id ON coaching(call_id);
"""


class SupabaseService:
    """Service class for all Supabase database operations."""

    def __init__(self):
        settings = get_settings()
        self.client: Client = create_client(settings.SUPABASE_URL, settings.SUPABASE_KEY)

    # ──────────── Calls ────────────

    def create_call(self, call_data: dict) -> dict:
        """Create a new call record."""
        call_data["created_at"] = get_utc_now()
        call_data["updated_at"] = get_utc_now()
        result = self.client.table("calls").insert(call_data).execute()
        return result.data[0] if result.data else {}

    def update_call_status(self, call_id: str, status: str, error: Optional[str] = None,
                           processing_time: Optional[float] = None) -> dict:
        """Update call status."""
        update_data = {"status": status, "updated_at": get_utc_now()}
        if error:
            update_data["error"] = error
        if processing_time is not None:
            update_data["processing_time_seconds"] = processing_time
        result = self.client.table("calls").update(update_data).eq("call_id", call_id).execute()
        return result.data[0] if result.data else {}

    def get_call(self, call_id: str) -> Optional[dict]:
        """Get a call by ID."""
        result = self.client.table("calls").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    def list_calls(self, page: int = 1, page_size: int = 20) -> tuple:
        """List calls with pagination."""
        offset = (page - 1) * page_size
        result = (
            self.client.table("calls")
            .select("*", count="exact")
            .order("created_at", desc=True)
            .range(offset, offset + page_size - 1)
            .execute()
        )
        return result.data or [], result.count or 0

    def delete_call(self, call_id: str) -> bool:
        """Delete a call and all related data (cascade)."""
        result = self.client.table("calls").delete().eq("call_id", call_id).execute()
        return len(result.data) > 0 if result.data else False

    # ──────────── Transcripts ────────────

    def save_transcript(self, call_id: str, transcript_data: dict) -> dict:
        """Save a transcript."""
        transcript_data["call_id"] = call_id
        transcript_data["created_at"] = get_utc_now()
        result = self.client.table("transcripts").insert(transcript_data).execute()
        return result.data[0] if result.data else {}

    def get_transcript(self, call_id: str) -> Optional[dict]:
        """Get transcript for a call."""
        result = self.client.table("transcripts").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Summaries ────────────

    def save_summary(self, call_id: str, summary_data: dict) -> dict:
        """Save a call summary."""
        summary_data["call_id"] = call_id
        summary_data["created_at"] = get_utc_now()
        result = self.client.table("summaries").insert(summary_data).execute()
        return result.data[0] if result.data else {}

    def get_summary(self, call_id: str) -> Optional[dict]:
        """Get summary for a call."""
        result = self.client.table("summaries").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Quality Scores ────────────

    def save_quality_scores(self, call_id: str, scores_data: dict) -> dict:
        """Save quality scores."""
        scores_data["call_id"] = call_id
        scores_data["created_at"] = get_utc_now()
        result = self.client.table("quality_scores").insert(scores_data).execute()
        return result.data[0] if result.data else {}

    def get_quality_scores(self, call_id: str) -> Optional[dict]:
        """Get quality scores for a call."""
        result = self.client.table("quality_scores").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Sentiments ────────────

    def save_sentiment(self, call_id: str, sentiment_data: dict) -> dict:
        """Save sentiment analysis."""
        sentiment_data["call_id"] = call_id
        sentiment_data["created_at"] = get_utc_now()
        result = self.client.table("sentiments").insert(sentiment_data).execute()
        return result.data[0] if result.data else {}

    def get_sentiment(self, call_id: str) -> Optional[dict]:
        """Get sentiment for a call."""
        result = self.client.table("sentiments").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Routing Decisions ────────────

    def save_routing(self, call_id: str, routing_data: dict) -> dict:
        """Save routing decision."""
        routing_data["call_id"] = call_id
        routing_data["created_at"] = get_utc_now()
        result = self.client.table("routing_decisions").insert(routing_data).execute()
        return result.data[0] if result.data else {}

    def get_routing(self, call_id: str) -> Optional[dict]:
        """Get routing decision for a call."""
        result = self.client.table("routing_decisions").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Coaching ────────────

    def save_coaching(self, call_id: str, coaching_data: dict) -> dict:
        """Save coaching recommendations."""
        coaching_data["call_id"] = call_id
        coaching_data["created_at"] = get_utc_now()
        result = self.client.table("coaching").insert(coaching_data).execute()
        return result.data[0] if result.data else {}

    def get_coaching(self, call_id: str) -> Optional[dict]:
        """Get coaching for a call."""
        result = self.client.table("coaching").select("*").eq("call_id", call_id).execute()
        return result.data[0] if result.data else None

    # ──────────── Full Analysis ────────────

    def get_full_analysis(self, call_id: str) -> Optional[dict]:
        """Get complete analysis for a call (all tables)."""
        call = self.get_call(call_id)
        if not call:
            return None

        return {
            "call": call,
            "transcript": self.get_transcript(call_id),
            "summary": self.get_summary(call_id),
            "quality_scores": self.get_quality_scores(call_id),
            "sentiment": self.get_sentiment(call_id),
            "routing": self.get_routing(call_id),
            "coaching": self.get_coaching(call_id),
        }

    # ──────────── Dashboard Stats ────────────

    def get_dashboard_stats(self) -> dict:
        """Get aggregated stats for the dashboard."""
        # Total calls
        calls_result = self.client.table("calls").select("*", count="exact").execute()
        total_calls = calls_result.count or 0

        # Recent calls
        recent = (
            self.client.table("calls")
            .select("*")
            .order("created_at", desc=True)
            .limit(10)
            .execute()
        )

        # Quality scores for averages
        scores = self.client.table("quality_scores").select("overall_score").execute()
        avg_score = None
        if scores.data:
            valid_scores = [s["overall_score"] for s in scores.data if s.get("overall_score")]
            avg_score = round(sum(valid_scores) / len(valid_scores), 2) if valid_scores else None

        # Sentiment distribution
        sentiments = self.client.table("sentiments").select("overall_sentiment").execute()
        sentiment_dist = {}
        if sentiments.data:
            for s in sentiments.data:
                label = s.get("overall_sentiment", "unknown")
                sentiment_dist[label] = sentiment_dist.get(label, 0) + 1

        # Category distribution
        routing = self.client.table("routing_decisions").select("category, urgency").execute()
        category_dist = {}
        urgency_dist = {}
        if routing.data:
            for r in routing.data:
                cat = r.get("category", "unknown")
                urg = r.get("urgency", "unknown")
                category_dist[cat] = category_dist.get(cat, 0) + 1
                urgency_dist[urg] = urgency_dist.get(urg, 0) + 1

        # Resolution rate
        resolution_data = self.client.table("routing_decisions").select("resolution_status").execute()
        resolution_rate = None
        if resolution_data.data:
            resolved = sum(1 for r in resolution_data.data if r.get("resolution_status") in ["resolved", "partially_resolved"])
            resolution_rate = round((resolved / len(resolution_data.data)) * 100, 1) if resolution_data.data else None

        return {
            "total_calls": total_calls,
            "avg_quality_score": avg_score,
            "avg_resolution_rate": resolution_rate,
            "sentiment_distribution": sentiment_dist,
            "category_distribution": category_dist,
            "urgency_distribution": urgency_dist,
            "recent_calls": recent.data or [],
        }


# Singleton instance
_supabase_service: Optional[SupabaseService] = None


def get_supabase_service() -> SupabaseService:
    """Get or create the Supabase service singleton."""
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service
