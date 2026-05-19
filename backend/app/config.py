"""
Application configuration using Pydantic Settings.
Loads environment variables from .env file.
"""

from pydantic_settings import BaseSettings
from typing import List
from functools import lru_cache


class Settings(BaseSettings):
    """Application settings loaded from environment variables."""

    # OpenAI
    OPENAI_API_KEY: str

    # Supabase
    SUPABASE_URL: str
    SUPABASE_KEY: str

    # Application
    APP_ENV: str = "development"
    APP_DEBUG: bool = True
    APP_HOST: str = "0.0.0.0"
    APP_PORT: int = 8000

    # Audio
    MAX_AUDIO_SIZE_MB: int = 50
    ALLOWED_AUDIO_FORMATS: str = "wav,mp3,m4a,webm,ogg,flac"

    # LLM
    GPT_MODEL_PRIMARY: str = "gpt-4o"
    GPT_MODEL_SECONDARY: str = "gpt-4o-mini"
    WHISPER_MODEL: str = "whisper-1"
    LLM_TEMPERATURE: float = 0.3
    LLM_MAX_RETRIES: int = 3

    # LangSmith Tracing
    LANGCHAIN_TRACING_V2: str = "false"
    LANGCHAIN_API_KEY: str = ""
    LANGCHAIN_PROJECT: str = "callsense-ai"
    LANGCHAIN_ENDPOINT: str = "https://api.smith.langchain.com"

    # Multi-language
    DEFAULT_LANGUAGE: str = "auto"
    SUPPORTED_LANGUAGES: str = "en,es,fr,de,hi,ja,zh,ar,pt,ko"

    @property
    def allowed_formats_list(self) -> List[str]:
        return [fmt.strip() for fmt in self.ALLOWED_AUDIO_FORMATS.split(",")]

    @property
    def max_audio_size_bytes(self) -> int:
        return self.MAX_AUDIO_SIZE_MB * 1024 * 1024

    @property
    def supported_languages_list(self) -> List[str]:
        return [lang.strip() for lang in self.SUPPORTED_LANGUAGES.split(",")]

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """Cached settings instance."""
    return Settings()
