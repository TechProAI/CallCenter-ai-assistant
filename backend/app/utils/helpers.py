"""
Utility helper functions for CallSense.
"""

import uuid
import json
import re
import logging
from datetime import datetime, timezone
from typing import Any, Optional

logger = logging.getLogger(__name__)


def generate_call_id() -> str:
    """Generate a unique call ID."""
    return f"call_{uuid.uuid4().hex[:12]}"


def get_utc_now() -> str:
    """Get current UTC timestamp as ISO string."""
    return datetime.now(timezone.utc).isoformat()


def parse_llm_json(response_text: str) -> dict:
    """
    Parse JSON from LLM response, handling common formatting issues.
    LLMs sometimes wrap JSON in markdown code blocks or add extra text.
    """
    if not response_text:
        raise ValueError("Empty response from LLM")

    text = response_text.strip()

    # Remove markdown code block wrappers
    if text.startswith("```json"):
        text = text[7:]
    elif text.startswith("```"):
        text = text[3:]
    if text.endswith("```"):
        text = text[:-3]

    text = text.strip()

    # Try direct parse first
    try:
        return json.loads(text)
    except json.JSONDecodeError:
        pass

    # Try to find JSON object in the text
    json_match = re.search(r'\{[\s\S]*\}', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    # Try to find JSON array
    json_match = re.search(r'\[[\s\S]*\]', text)
    if json_match:
        try:
            return json.loads(json_match.group())
        except json.JSONDecodeError:
            pass

    raise ValueError(f"Could not parse JSON from LLM response: {text[:200]}...")


def calculate_overall_quality_score(scores: dict) -> float:
    """
    Calculate weighted overall quality score.
    Weights: Empathy(20%), Professionalism(15%), Resolution(25%),
    Communication(15%), Compliance(10%), Active Listening(15%)
    """
    weights = {
        "empathy_score": 0.20,
        "professionalism_score": 0.15,
        "resolution_score": 0.25,
        "communication_score": 0.15,
        "compliance_score": 0.10,
        "active_listening_score": 0.15,
    }

    total = 0.0
    for key, weight in weights.items():
        score_data = scores.get(key, {})
        score_value = score_data.get("score", 0) if isinstance(score_data, dict) else 0
        total += score_value * weight

    return round(total, 2)


def score_to_grade(score: float) -> str:
    """Convert numeric score (0-10) to letter grade."""
    if score >= 8:
        return "A"
    elif score >= 6:
        return "B"
    elif score >= 4:
        return "C"
    elif score >= 2:
        return "D"
    else:
        return "F"


def format_file_size(size_bytes: int) -> str:
    """Format file size in human readable format."""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    else:
        return f"{size_bytes / (1024 * 1024):.1f} MB"


def truncate_text(text: str, max_length: int = 500) -> str:
    """Truncate text to max length with ellipsis."""
    if len(text) <= max_length:
        return text
    return text[:max_length - 3] + "..."


def validate_audio_format(filename: str, allowed_formats: list) -> bool:
    """Check if the audio file format is allowed."""
    if not filename:
        return False
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    return ext in allowed_formats


def safe_get(data: dict, *keys, default: Any = None) -> Any:
    """Safely get nested dictionary values."""
    current = data
    for key in keys:
        if isinstance(current, dict):
            current = current.get(key, default)
        else:
            return default
    return current
