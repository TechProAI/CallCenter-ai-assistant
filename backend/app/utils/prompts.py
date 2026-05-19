"""
Prompt templates for all CallSense agents.
Each prompt is carefully crafted for structured, reliable LLM outputs.
"""

SUMMARIZATION_PROMPT = """You are an expert call center analyst. Analyze the following call transcript and produce a structured summary.

<transcript>
{transcript}
</transcript>

Provide your analysis as a JSON object with exactly these fields:
{{
    "brief_summary": "2-3 sentence overview of what happened in this call",
    "detailed_summary": "A thorough paragraph covering all important details discussed",
    "key_points": ["point 1", "point 2", ...],
    "customer_intent": "The primary reason the customer called",
    "action_items": ["action 1", "action 2", ...],
    "issues_raised": ["issue 1", "issue 2", ...],
    "resolution_provided": "How the agent addressed or attempted to resolve the customer's concerns",
    "follow_up_needed": true/false,
    "follow_up_details": "Details about required follow-up, or null if not needed"
}}

Rules:
- Be objective and factual — only include information present in the transcript.
- Key points should be concise but informative.
- Action items should be specific and actionable.
- If resolution was not achieved, clearly state what was left unresolved.
- Respond ONLY with valid JSON, no additional text."""


QUALITY_SCORING_PROMPT = """You are a senior Quality Assurance evaluator for a call center. Evaluate the following call transcript across multiple quality dimensions.

<transcript>
{transcript}
</transcript>

Score each dimension from 0-10 and provide detailed justification. Respond as a JSON object:
{{
    "empathy_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples from the call"],
        "improvements": ["What could be improved"]
    }},
    "professionalism_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples"],
        "improvements": ["Areas for improvement"]
    }},
    "resolution_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples"],
        "improvements": ["Areas for improvement"]
    }},
    "communication_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples"],
        "improvements": ["Areas for improvement"]
    }},
    "compliance_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples"],
        "improvements": ["Areas for improvement"]
    }},
    "active_listening_score": {{
        "score": <0-10>,
        "justification": "Why this score was given",
        "highlights": ["Positive examples"],
        "improvements": ["Areas for improvement"]
    }},
    "overall_score": <weighted average, 0-10>,
    "grade": "<A/B/C/D/F based on overall_score: A=8-10, B=6-7.9, C=4-5.9, D=2-3.9, F=0-1.9>",
    "overall_feedback": "Comprehensive feedback paragraph covering performance"
}}

Scoring Guidelines:
- Empathy: Did the agent acknowledge the customer's feelings and frustrations?
- Professionalism: Was the agent courteous, patient, and professional throughout?
- Resolution: Was the issue effectively resolved or properly escalated?
- Communication: Was the agent clear, concise, and easy to understand?
- Compliance: Did the agent follow standard protocols (greeting, verification, closing)?
- Active Listening: Did the agent address what the customer actually said vs. giving generic responses?

Weighting for overall_score: Empathy(20%), Professionalism(15%), Resolution(25%), Communication(15%), Compliance(10%), Active Listening(15%)

Respond ONLY with valid JSON."""


SENTIMENT_ANALYSIS_PROMPT = """You are a sentiment analysis expert specializing in customer service interactions. Analyze the emotional dynamics of this call transcript.

<transcript>
{transcript}
</transcript>

Provide your analysis as a JSON object:
{{
    "overall_sentiment": "<very_positive|positive|neutral|negative|very_negative>",
    "overall_confidence": <0.0-1.0>,
    "customer_sentiment": "<very_positive|positive|neutral|negative|very_negative>",
    "agent_sentiment": "<very_positive|positive|neutral|negative|very_negative>",
    "sentiment_trajectory": "<improved|declined|stable|mixed>",
    "phases": [
        {{
            "phase": "opening",
            "sentiment": "<very_positive|positive|neutral|negative|very_negative>",
            "confidence": <0.0-1.0>,
            "key_phrases": ["phrases indicating this sentiment"]
        }},
        {{
            "phase": "issue_description",
            "sentiment": "<sentiment>",
            "confidence": <0.0-1.0>,
            "key_phrases": ["relevant phrases"]
        }},
        {{
            "phase": "resolution",
            "sentiment": "<sentiment>",
            "confidence": <0.0-1.0>,
            "key_phrases": ["relevant phrases"]
        }},
        {{
            "phase": "closing",
            "sentiment": "<sentiment>",
            "confidence": <0.0-1.0>,
            "key_phrases": ["relevant phrases"]
        }}
    ],
    "emotional_triggers": ["Events or statements that caused notable sentiment shifts"]
}}

Rules:
- Analyze customer and agent sentiment separately.
- Identify the trajectory — did the customer's mood improve or worsen?
- Include only phases that are present in the transcript.
- Key phrases should be brief excerpts or paraphrases from the transcript.
- Respond ONLY with valid JSON."""


ROUTING_PROMPT = """You are a call center routing and categorization specialist. Analyze this call transcript and determine the appropriate routing, categorization, and priority.

<transcript>
{transcript}
</transcript>

<summary>
{summary}
</summary>

<quality_score>
{quality_score}
</quality_score>

Provide your routing decision as a JSON object:
{{
    "category": "<billing|technical_support|account_management|complaints|general_inquiry|sales|cancellation|feedback|escalation|other>",
    "urgency": "<low|medium|high|critical>",
    "resolution_status": "<resolved|partially_resolved|unresolved|follow_up_required|escalated>",
    "requires_escalation": true/false,
    "escalation_reason": "Reason for escalation if applicable, null otherwise",
    "recommended_department": "Department that should handle follow-up if needed, null otherwise",
    "tags": ["descriptive", "tags", "for", "this", "call"],
    "priority_score": <1-10, where 10 is highest priority>
}}

Urgency Guidelines:
- Critical: Customer threatening legal action, regulatory issue, service outage affecting many
- High: Billing disputes, unresolved complaints, repeated calls for same issue
- Medium: Standard service requests, general complaints, account changes
- Low: General inquiries, positive feedback, routine questions

Respond ONLY with valid JSON."""


COACHING_PROMPT = """You are a senior call center coach and trainer. Based on the call analysis below, provide actionable coaching recommendations for the agent.

<transcript>
{transcript}
</transcript>

<quality_scores>
{quality_scores}
</quality_scores>

<sentiment>
{sentiment}
</sentiment>

Provide coaching recommendations as a JSON object:
{{
    "strengths": ["Specific things the agent did well with examples"],
    "areas_for_improvement": ["Specific areas where the agent can improve"],
    "training_suggestions": ["Recommended training topics or modules"],
    "example_responses": ["Better alternative responses the agent could have used in specific moments"],
    "overall_recommendation": "A comprehensive coaching summary paragraph"
}}

Rules:
- Be constructive and specific — reference actual moments from the call.
- Strengths should highlight genuinely good behaviors worth reinforcing.
- Improvements should be actionable, not vague.
- Example responses should show what the agent could say differently in specific situations from the call.
- Training suggestions should be practical and relevant.
- Respond ONLY with valid JSON."""


SPEAKER_DIARIZATION_PROMPT = """You are a transcript analysis expert. Analyze this raw transcript and identify different speakers (typically a customer and an agent). Reformat the transcript with speaker labels.

<transcript>
{transcript}
</transcript>

Provide the diarized transcript as a JSON object:
{{
    "segments": [
        {{
            "speaker": "Agent" or "Customer",
            "text": "What they said"
        }}
    ],
    "speaker_count": <number of distinct speakers>,
    "agent_talk_ratio": <0.0-1.0, percentage of conversation from agent>,
    "customer_talk_ratio": <0.0-1.0, percentage of conversation from customer>
}}

Rules:
- Identify speakers based on context clues (greetings, role references, question patterns).
- If the transcript already has speaker labels, preserve them.
- If you cannot determine speakers, label them as "Speaker 1", "Speaker 2", etc.
- Respond ONLY with valid JSON."""
