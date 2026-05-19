"""
Audio service for handling file uploads and processing.
"""

import os
import tempfile
import logging
from typing import Optional, Tuple

from app.config import get_settings
from app.utils.helpers import validate_audio_format

logger = logging.getLogger(__name__)

UPLOAD_DIR = os.path.join(tempfile.gettempdir(), "callsense_uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)


class AudioService:
    """Service for audio file operations."""

    def __init__(self):
        settings = get_settings()
        self.max_size = settings.max_audio_size_bytes
        self.allowed_formats = settings.allowed_formats_list

    async def save_upload(self, file_content: bytes, filename: str) -> Tuple[str, dict]:
        """
        Save an uploaded audio file to temp storage.
        Returns (file_path, metadata).
        """
        # Validate format
        if not validate_audio_format(filename, self.allowed_formats):
            raise ValueError(
                f"Invalid audio format. Allowed: {', '.join(self.allowed_formats)}"
            )

        # Validate size
        if len(file_content) > self.max_size:
            settings = get_settings()
            raise ValueError(
                f"File too large. Maximum size: {settings.MAX_AUDIO_SIZE_MB}MB"
            )

        # Save to temp directory
        ext = filename.rsplit(".", 1)[-1].lower()
        temp_path = os.path.join(UPLOAD_DIR, f"upload_{os.urandom(8).hex()}.{ext}")

        with open(temp_path, "wb") as f:
            f.write(file_content)

        metadata = {
            "file_name": filename,
            "file_size_bytes": len(file_content),
            "audio_format": ext,
            "file_path": temp_path,
        }

        # Try to get duration using pydub
        duration = self._get_duration(temp_path, ext)
        if duration:
            metadata["duration_seconds"] = duration

        logger.info(f"Saved audio file: {filename} ({len(file_content)} bytes)")
        return temp_path, metadata

    def _get_duration(self, file_path: str, ext: str) -> Optional[float]:
        """Get audio duration in seconds."""
        try:
            from pydub import AudioSegment

            format_map = {"m4a": "m4a", "webm": "webm", "ogg": "ogg"}
            fmt = format_map.get(ext, ext)

            audio = AudioSegment.from_file(file_path, format=fmt)
            return round(len(audio) / 1000.0, 2)
        except Exception as e:
            logger.warning(f"Could not determine audio duration: {e}")
            return None

    def cleanup(self, file_path: str) -> None:
        """Remove a temporary audio file."""
        try:
            if os.path.exists(file_path):
                os.remove(file_path)
                logger.debug(f"Cleaned up: {file_path}")
        except Exception as e:
            logger.warning(f"Failed to cleanup {file_path}: {e}")


# Singleton
_audio_service: Optional[AudioService] = None


def get_audio_service() -> AudioService:
    """Get or create the Audio service singleton."""
    global _audio_service
    if _audio_service is None:
        _audio_service = AudioService()
    return _audio_service
