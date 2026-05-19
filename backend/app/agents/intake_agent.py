"""
Call Intake Agent — validates and preprocesses incoming calls.
First agent in the pipeline. Handles both audio uploads and transcript pastes.
"""

import logging
from typing import Optional

from app.models.schemas import CallIntakeResult, CallMetadata, CallStatus
from app.services.audio_service import get_audio_service
from app.utils.helpers import generate_call_id

logger = logging.getLogger(__name__)


class IntakeAgent:
    """Validates incoming call data and prepares it for processing."""

    def __init__(self):
        self.audio_service = get_audio_service()

    async def process_audio(self, file_content: bytes, filename: str) -> CallIntakeResult:
        """Process an audio file upload."""
        call_id = generate_call_id()
        try:
            file_path, metadata = await self.audio_service.save_upload(file_content, filename)

            return CallIntakeResult(
                call_id=call_id,
                metadata=CallMetadata(
                    file_name=metadata.get("file_name"),
                    file_size_bytes=metadata.get("file_size_bytes"),
                    audio_format=metadata.get("audio_format"),
                    duration_seconds=metadata.get("duration_seconds"),
                    source="upload",
                ),
                is_valid=True,
                validation_message="Audio file validated successfully.",
                input_type="audio",
            )
        except ValueError as e:
            return CallIntakeResult(
                call_id=call_id,
                metadata=CallMetadata(file_name=filename, source="upload"),
                is_valid=False,
                validation_message=str(e),
                input_type="audio",
            )
        except Exception as e:
            logger.error(f"Intake error for audio: {e}")
            return CallIntakeResult(
                call_id=call_id,
                metadata=CallMetadata(file_name=filename, source="upload"),
                is_valid=False,
                validation_message=f"Unexpected error during intake: {str(e)}",
                input_type="audio",
            )

    def process_transcript(
        self,
        transcript: str,
        caller_name: Optional[str] = None,
        agent_name: Optional[str] = None,
        call_date: Optional[str] = None,
    ) -> CallIntakeResult:
        """Process a directly submitted transcript."""
        call_id = generate_call_id()

        # Validate transcript
        if not transcript or len(transcript.strip()) < 50:
            return CallIntakeResult(
                call_id=call_id,
                metadata=CallMetadata(source="transcript_paste"),
                is_valid=False,
                validation_message="Transcript too short. Minimum 50 characters required.",
                input_type="transcript",
            )

        if len(transcript) > 100000:
            return CallIntakeResult(
                call_id=call_id,
                metadata=CallMetadata(source="transcript_paste"),
                is_valid=False,
                validation_message="Transcript too long. Maximum 100,000 characters.",
                input_type="transcript",
            )

        return CallIntakeResult(
            call_id=call_id,
            metadata=CallMetadata(source="transcript_paste"),
            is_valid=True,
            validation_message="Transcript validated successfully.",
            input_type="transcript",
        )
