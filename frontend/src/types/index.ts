// ── Enums ──

export type CallStatus = 'pending' | 'processing' | 'transcribing' | 'summarizing' | 'scoring' | 'analyzing' | 'completed' | 'failed';
export type CallCategory = 'billing' | 'technical_support' | 'account_management' | 'complaints' | 'general_inquiry' | 'sales' | 'cancellation' | 'feedback' | 'escalation' | 'other';
export type SentimentLabel = 'very_positive' | 'positive' | 'neutral' | 'negative' | 'very_negative';
export type UrgencyLevel = 'low' | 'medium' | 'high' | 'critical';
export type ResolutionStatus = 'resolved' | 'partially_resolved' | 'unresolved' | 'follow_up_required' | 'escalated';

// ── Transcript ──

export interface TranscriptSegment {
  speaker: string | null;
  text: string;
  start_time: number | null;
  end_time: number | null;
}

export interface Transcript {
  call_id: string;
  full_text: string;
  segments: TranscriptSegment[];
  language: string;
  confidence: number | null;
  duration_seconds: number | null;
}

// ── Summary ──

export interface Summary {
  call_id: string;
  brief_summary: string;
  detailed_summary: string;
  key_points: string[];
  customer_intent: string;
  action_items: string[];
  issues_raised: string[];
  resolution_provided: string;
  follow_up_needed: boolean;
  follow_up_details: string | null;
}

// ── Quality Scores ──

export interface ScoreBreakdown {
  score: number;
  justification: string;
  highlights: string[];
  improvements: string[];
}

export interface QualityScores {
  call_id: string;
  empathy_score: ScoreBreakdown;
  professionalism_score: ScoreBreakdown;
  resolution_score: ScoreBreakdown;
  communication_score: ScoreBreakdown;
  compliance_score: ScoreBreakdown;
  active_listening_score: ScoreBreakdown;
  overall_score: number;
  grade: string;
  overall_feedback: string;
}

// ── Sentiment ──

export interface SentimentPhase {
  phase: string;
  sentiment: SentimentLabel;
  confidence: number;
  key_phrases: string[];
}

export interface SentimentAnalysis {
  call_id: string;
  overall_sentiment: SentimentLabel;
  overall_confidence: number;
  customer_sentiment: SentimentLabel;
  agent_sentiment: SentimentLabel;
  sentiment_trajectory: string;
  phases: SentimentPhase[];
  emotional_triggers: string[];
}

// ── Routing ──

export interface RoutingDecision {
  call_id: string;
  category: CallCategory;
  urgency: UrgencyLevel;
  resolution_status: ResolutionStatus;
  requires_escalation: boolean;
  escalation_reason: string | null;
  recommended_department: string | null;
  tags: string[];
  priority_score: number;
}

// ── Coaching ──

export interface CoachingRecommendation {
  call_id: string;
  strengths: string[];
  areas_for_improvement: string[];
  training_suggestions: string[];
  example_responses: string[];
  overall_recommendation: string;
}

// ── Full Analysis ──

export interface CallRecord {
  call_id: string;
  status: CallStatus;
  input_type: string;
  file_name: string | null;
  file_size_bytes: number | null;
  audio_format: string | null;
  duration_seconds: number | null;
  source: string;
  caller_name: string | null;
  agent_name: string | null;
  error: string | null;
  processing_time_seconds: number | null;
  created_at: string;
  updated_at: string;
}

export interface FullAnalysis {
  call: CallRecord;
  transcript: Transcript | null;
  summary: Summary | null;
  quality_scores: QualityScores | null;
  sentiment: SentimentAnalysis | null;
  routing: RoutingDecision | null;
  coaching: CoachingRecommendation | null;
}

// ── API Responses ──

export interface AnalysisStatus {
  call_id: string;
  status: CallStatus;
  message: string;
  progress_percent: number | null;
}

export interface CallListItem {
  call_id: string;
  status: CallStatus;
  category: CallCategory | null;
  overall_score: number | null;
  overall_sentiment: SentimentLabel | null;
  brief_summary: string | null;
  urgency: UrgencyLevel | null;
  resolution_status: ResolutionStatus | null;
  created_at: string;
  duration_seconds: number | null;
}

export interface DashboardStats {
  total_calls: number;
  avg_quality_score: number | null;
  avg_resolution_rate: number | null;
  sentiment_distribution: Record<string, number>;
  category_distribution: Record<string, number>;
  urgency_distribution: Record<string, number>;
  recent_calls: CallRecord[];
}
