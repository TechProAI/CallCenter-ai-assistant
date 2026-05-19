"""
Pydantic schemas for structured data models.
Used for API request/response validation and LLM structured outputs.
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from enum import Enum
from datetime import datetime


# ──────────────────────────────────────────────
# Enums
# ──────────────────────────────────────────────

class CallStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    TRANSCRIBING = "transcribing"
    SUMMARIZING = "summarizing"
    SCORING = "scoring"
    ANALYZING = "analyzing"
    COMPLETED = "completed"
    FAILED = "failed"


class CallCategory(str, Enum):
    BILLING = "billing"
    TECHNICAL_SUPPORT = "technical_support"
    ACCOUNT_MANAGEMENT = "account_management"
    COMPLAINTS = "complaints"
    GENERAL_INQUIRY = "general_inquiry"
    SALES = "sales"
    CANCELLATION = "cancellation"
    FEEDBACK = "feedback"
    ESCALATION = "escalation"
    OTHER = "other"


class SentimentLabel(str, Enum):
    VERY_POSITIVE = "very_positive"
    POSITIVE = "positive"
    NEUTRAL = "neutral"
    NEGATIVE = "negative"
    VERY_NEGATIVE = "very_negative"


class UrgencyLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class ResolutionStatus(str, Enum):
    RESOLVED = "resolved"
    PARTIALLY_RESOLVED = "partially_resolved"
    UNRESOLVED = "unresolved"
    FOLLOW_UP_REQUIRED = "follow_up_required"
    ESCALATED = "escalated"


# ──────────────────────────────────────────────
# Call Intake Schemas
# ──────────────────────────────────────────────

class CallMetadata(BaseModel):
    """Metadata extracted during call intake."""
    file_name: Optional[str] = None
    file_size_bytes: Optional[int] = None
    audio_format: Optional[str] = None
    duration_seconds: Optional[float] = None
    source: str = "upload"  # upload, api, transcript_paste


class CallIntakeResult(BaseModel):
    """Result from the Call Intake Agent."""
    call_id: str
    metadata: CallMetadata
    is_valid: bool
    validation_message: str
    input_type: str  # "audio" or "transcript"


# ──────────────────────────────────────────────
# Transcription Schemas
# ──────────────────────────────────────────────

class TranscriptSegment(BaseModel):
    """A segment of the transcript with timing."""
    speaker: Optional[str] = None
    text: str
    start_time: Optional[float] = None
    end_time: Optional[float] = None


class TranscriptionResult(BaseModel):
    """Result from the Transcription Agent."""
    call_id: str
    full_text: str
    segments: List[TranscriptSegment] = []
    language: str = "en"
    confidence: Optional[float] = None
    duration_seconds: Optional[float] = None


# ──────────────────────────────────────────────
# Summarization Schemas
# ──────────────────────────────────────────────

class CallSummary(BaseModel):
    """Structured summary from the Summarization Agent."""
    call_id: str
    brief_summary: str = Field(description="2-3 sentence overview of the call")
    detailed_summary: str = Field(description="Detailed summary covering all key points")
    key_points: List[str] = Field(description="Bullet points of key discussion topics")
    customer_intent: str = Field(description="Primary reason the customer called")
    action_items: List[str] = Field(description="Action items identified from the call")
    issues_raised: List[str] = Field(description="Problems or issues mentioned by the customer")
    resolution_provided: str = Field(description="How the agent addressed the customer's concerns")
    follow_up_needed: bool = Field(description="Whether follow-up action is required")
    follow_up_details: Optional[str] = Field(default=None, description="Details on follow-up if needed")


# ──────────────────────────────────────────────
# Quality Scoring Schemas
# ──────────────────────────────────────────────

class ScoreBreakdown(BaseModel):
    """Individual score with justification."""
    score: float = Field(ge=0, le=10, description="Score from 0-10")
    justification: str = Field(description="Reason for the score")
    highlights: List[str] = Field(default=[], description="Positive examples from the call")
    improvements: List[str] = Field(default=[], description="Areas for improvement")


class QualityScores(BaseModel):
    """Quality scores from the Quality Scoring Agent."""
    call_id: str
    empathy_score: ScoreBreakdown = Field(description="How well the agent showed empathy")
    professionalism_score: ScoreBreakdown = Field(description="Level of professionalism maintained")
    resolution_score: ScoreBreakdown = Field(description="Effectiveness of issue resolution")
    communication_score: ScoreBreakdown = Field(description="Clarity and effectiveness of communication")
    compliance_score: ScoreBreakdown = Field(description="Adherence to protocols and compliance")
    active_listening_score: ScoreBreakdown = Field(description="How well the agent listened to the customer")
    overall_score: float = Field(ge=0, le=10, description="Weighted overall score")
    grade: str = Field(description="Letter grade: A, B, C, D, F")
    overall_feedback: str = Field(description="General performance feedback")


# ──────────────────────────────────────────────
# Sentiment Analysis Schemas
# ──────────────────────────────────────────────

class SentimentPhase(BaseModel):
    """Sentiment for a phase of the call."""
    phase: str = Field(description="e.g., opening, issue_description, resolution, closing")
    sentiment: SentimentLabel
    confidence: float = Field(ge=0, le=1)
    key_phrases: List[str] = Field(default=[], description="Phrases indicating this sentiment")


class SentimentAnalysis(BaseModel):
    """Sentiment analysis from the Sentiment Agent."""
    call_id: str
    overall_sentiment: SentimentLabel
    overall_confidence: float = Field(ge=0, le=1)
    customer_sentiment: SentimentLabel
    agent_sentiment: SentimentLabel
    sentiment_trajectory: str = Field(description="How sentiment changed: improved, declined, stable, mixed")
    phases: List[SentimentPhase] = []
    emotional_triggers: List[str] = Field(default=[], description="Events that shifted sentiment")


# ──────────────────────────────────────────────
# Routing Schemas
# ──────────────────────────────────────────────

class RoutingDecision(BaseModel):
    """Routing decision from the Routing Agent."""
    call_id: str
    category: CallCategory
    urgency: UrgencyLevel
    resolution_status: ResolutionStatus
    requires_escalation: bool
    escalation_reason: Optional[str] = None
    recommended_department: Optional[str] = None
    tags: List[str] = Field(default=[], description="Descriptive tags for the call")
    priority_score: int = Field(ge=1, le=10, description="Priority ranking 1-10")


# ──────────────────────────────────────────────
# Recommendation Schemas (Creative Addition)
# ──────────────────────────────────────────────

class CoachingRecommendation(BaseModel):
    """Coaching recommendations for the call center agent."""
    call_id: str
    strengths: List[str] = Field(description="What the agent did well")
    areas_for_improvement: List[str] = Field(description="Specific areas to work on")
    training_suggestions: List[str] = Field(description="Recommended training modules or resources")
    example_responses: List[str] = Field(default=[], description="Better alternative responses the agent could have used")
    overall_recommendation: str = Field(description="Summary coaching recommendation")


# ──────────────────────────────────────────────
# Complete Analysis Result
# ──────────────────────────────────────────────

class CallAnalysisResult(BaseModel):
    """Complete analysis result combining all agent outputs."""
    call_id: str
    status: CallStatus
    metadata: CallMetadata
    transcript: Optional[TranscriptionResult] = None
    summary: Optional[CallSummary] = None
    quality_scores: Optional[QualityScores] = None
    sentiment: Optional[SentimentAnalysis] = None
    routing: Optional[RoutingDecision] = None
    coaching: Optional[CoachingRecommendation] = None
    processing_time_seconds: Optional[float] = None
    error: Optional[str] = None
    created_at: Optional[str] = None


# ──────────────────────────────────────────────
# API Request/Response Schemas
# ──────────────────────────────────────────────

class TranscriptInput(BaseModel):
    """Request body for submitting a raw transcript."""
    transcript: str = Field(min_length=50, description="The call transcript text")
    caller_name: Optional[str] = None
    agent_name: Optional[str] = None
    call_date: Optional[str] = None
    language: Optional[str] = Field(default="auto", description="Language code e.g. en, es, fr, hi. Use 'auto' for auto-detection.")


class CallListItem(BaseModel):
    """Summary item for the calls list."""
    call_id: str
    status: CallStatus
    category: Optional[CallCategory] = None
    overall_score: Optional[float] = None
    overall_sentiment: Optional[SentimentLabel] = None
    brief_summary: Optional[str] = None
    urgency: Optional[UrgencyLevel] = None
    resolution_status: Optional[ResolutionStatus] = None
    created_at: str
    duration_seconds: Optional[float] = None


class CallListResponse(BaseModel):
    """Response for listing calls."""
    calls: List[CallListItem]
    total_count: int
    page: int = 1
    page_size: int = 20


class DashboardStats(BaseModel):
    """Dashboard statistics."""
    total_calls: int
    avg_quality_score: Optional[float] = None
    avg_resolution_rate: Optional[float] = None
    sentiment_distribution: Dict[str, int] = {}
    category_distribution: Dict[str, int] = {}
    urgency_distribution: Dict[str, int] = {}
    recent_calls: List[CallListItem] = []
    score_trend: List[Dict[str, Any]] = []


class AnalysisStatusResponse(BaseModel):
    """Response for checking analysis status."""
    call_id: str
    status: CallStatus
    message: str
    progress_percent: Optional[int] = None
