"""
Transcription Agent — converts audio to text using Whisper API.
Also performs speaker diarization using LLM.
"""

import logging
from typing import Optional

from app.models.schemas import TranscriptionResult, TranscriptSegment
from app.services.openai_service import get_openai_service

logger = logging.getLogger(__name__)


class TranscriptionAgent:
    """Handles audio-to-text transcription and speaker identification."""

    def __init__(self):
        self.openai_service = get_openai_service()

    def transcribe_audio(self, audio_file_path: str, call_id: str) -> TranscriptionResult:
        """Transcribe an audio file and perform diarization."""
        logger.info(f"[{call_id}] Starting transcription...")

        # Step 1: Whisper transcription
        whisper_result = self.openai_service.transcribe_audio(audio_file_path)

        full_text = whisper_result.get("text", "")
        if not full_text:
            raise ValueError("Transcription returned empty text")

        # Step 2: Speaker diarization via LLM
        segments = self._diarize(full_text, call_id)

        result = TranscriptionResult(
            call_id=call_id,
            full_text=full_text,
            segments=segments,
            language=whisper_result.get("language", "en"),
            confidence=None,
            duration_seconds=whisper_result.get("duration"),
        )

        logger.info(
            f"[{call_id}] Transcription complete: {len(full_text)} chars, "
            f"{len(segments)} segments"
        )
        return result

    def process_transcript(self, transcript: str, call_id: str) -> TranscriptionResult:
        """Process a pre-existing transcript (diarize only)."""
        logger.info(f"[{call_id}] Processing provided transcript...")

        segments = self._diarize(transcript, call_id)

        return TranscriptionResult(
            call_id=call_id,
            full_text=transcript,
            segments=segments,
            language="en",
            confidence=None,
            duration_seconds=None,
        )

    def _diarize(self, transcript: str, call_id: str) -> list:
        """Perform speaker diarization using LLM."""
        try:
            diarization = self.openai_service.diarize_transcript(transcript)
            segments = []
            for seg in diarization.get("segments", []):
                segments.append(
                    TranscriptSegment(
                        speaker=seg.get("speaker", "Unknown"),
                        text=seg.get("text", ""),
                        start_time=seg.get("start_time"),
                        end_time=seg.get("end_time"),
                    )
                )
            logger.info(f"[{call_id}] Diarization: {len(segments)} segments identified")
            return segments
        except Exception as e:
            logger.warning(f"[{call_id}] Diarization failed, using raw transcript: {e}")
            return [TranscriptSegment(speaker="Unknown", text=transcript)]
