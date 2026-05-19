"""
OpenAI service for LLM completions and Whisper transcription.
Handles retries, error handling, and model fallback.
"""

import logging
from typing import Optional
from openai import OpenAI
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from app.config import get_settings
from app.utils.helpers import parse_llm_json

logger = logging.getLogger(__name__)


class OpenAIService:
    """Service class for OpenAI API operations."""

    def __init__(self):
        settings = get_settings()
        self.client = OpenAI(api_key=settings.OPENAI_API_KEY)
        self.primary_model = settings.GPT_MODEL_PRIMARY
        self.secondary_model = settings.GPT_MODEL_SECONDARY
        self.whisper_model = settings.WHISPER_MODEL
        self.temperature = settings.LLM_TEMPERATURE
        self.max_retries = settings.LLM_MAX_RETRIES

    @retry(
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=2, max=10),
        retry=retry_if_exception_type((Exception,)),
        before_sleep=lambda retry_state: logger.warning(
            f"Retrying LLM call (attempt {retry_state.attempt_number})..."
        ),
    )
    def get_completion(
        self,
        prompt: str,
        system_message: str = "You are an expert call center analyst.",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
    ) -> str:
        """
        Get a completion from OpenAI.
        Uses primary model with fallback to secondary on failure.
        """
        model = model or self.primary_model
        temperature = temperature if temperature is not None else self.temperature

        try:
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": prompt},
                ],
                temperature=temperature,
                max_tokens=max_tokens,
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            # Fallback to secondary model
            if model == self.primary_model:
                logger.warning(f"Primary model failed ({e}), falling back to {self.secondary_model}")
                return self.get_completion(
                    prompt=prompt,
                    system_message=system_message,
                    model=self.secondary_model,
                    temperature=temperature,
                    max_tokens=max_tokens,
                )
            raise

    def get_json_completion(
        self,
        prompt: str,
        system_message: str = "You are an expert call center analyst. Respond ONLY with valid JSON.",
        model: Optional[str] = None,
        temperature: Optional[float] = None,
        max_tokens: int = 4096,
    ) -> dict:
        """Get a structured JSON completion from OpenAI."""
        raw_response = self.get_completion(
            prompt=prompt,
            system_message=system_message,
            model=model,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return parse_llm_json(raw_response)

    def transcribe_audio(self, audio_file_path: str, language: Optional[str] = None) -> dict:
        """
        Transcribe an audio file using Whisper API.
        Returns transcript text and metadata.
        """
        try:
            with open(audio_file_path, "rb") as audio_file:
                params = {
                    "model": self.whisper_model,
                    "file": audio_file,
                    "response_format": "verbose_json",
                }
                if language:
                    params["language"] = language

                response = self.client.audio.transcriptions.create(**params)

            result = {
                "text": response.text,
                "language": getattr(response, "language", "en"),
                "duration": getattr(response, "duration", None),
                "segments": [],
            }

            # Extract segments if available
            if hasattr(response, "segments") and response.segments:
                result["segments"] = [
                    {
                        "text": seg.get("text", "") if isinstance(seg, dict) else getattr(seg, "text", ""),
                        "start": seg.get("start", 0) if isinstance(seg, dict) else getattr(seg, "start", 0),
                        "end": seg.get("end", 0) if isinstance(seg, dict) else getattr(seg, "end", 0),
                    }
                    for seg in response.segments
                ]

            logger.info(f"Transcription complete: {len(result['text'])} chars, language={result['language']}")
            return result

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            raise

    def diarize_transcript(self, transcript: str) -> dict:
        """Use LLM to perform speaker diarization on a transcript."""
        from app.utils.prompts import SPEAKER_DIARIZATION_PROMPT

        prompt = SPEAKER_DIARIZATION_PROMPT.format(transcript=transcript)
        return self.get_json_completion(
            prompt=prompt,
            system_message="You are a transcript analysis expert. Identify speakers and format the transcript.",
        )


# Singleton instance
_openai_service: Optional[OpenAIService] = None


def get_openai_service() -> OpenAIService:
    """Get or create the OpenAI service singleton."""
    global _openai_service
    if _openai_service is None:
        _openai_service = OpenAIService()
    return _openai_service
