"""
CallSense API — AI-powered Call Center Analysis Platform.
Main FastAPI application entry point.
"""

import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers.calls import router as calls_router
from app.routers.dashboard import router as dashboard_router

# ──────────────────────────────────────────────
# Logging Configuration
# ──────────────────────────────────────────────

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


# ──────────────────────────────────────────────
# App Lifespan
# ──────────────────────────────────────────────

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application startup and shutdown events."""
    settings = get_settings()

    # Configure LangSmith tracing
    if settings.LANGCHAIN_TRACING_V2 == "true" and settings.LANGCHAIN_API_KEY:
        import os
        os.environ["LANGCHAIN_TRACING_V2"] = "true"
        os.environ["LANGCHAIN_API_KEY"] = settings.LANGCHAIN_API_KEY
        os.environ["LANGCHAIN_PROJECT"] = settings.LANGCHAIN_PROJECT
        os.environ["LANGCHAIN_ENDPOINT"] = settings.LANGCHAIN_ENDPOINT
        logger.info(f"  LangSmith tracing ENABLED (project: {settings.LANGCHAIN_PROJECT})")
    else:
        logger.info("  LangSmith tracing disabled")

    logger.info("=" * 60)
    logger.info("  CallSense API Starting")
    logger.info(f"  Environment: {settings.APP_ENV}")
    logger.info(f"  Primary Model: {settings.GPT_MODEL_PRIMARY}")
    logger.info(f"  Secondary Model: {settings.GPT_MODEL_SECONDARY}")
    logger.info("=" * 60)
    yield
    logger.info("CallSense API shutting down...")


# ──────────────────────────────────────────────
# FastAPI App
# ──────────────────────────────────────────────

app = FastAPI(
    title="CallSense API",
    description=(
        "AI-powered call center analysis platform. "
        "Upload audio or transcripts to get automated summaries, "
        "quality scores, sentiment analysis, routing decisions, "
        "and coaching recommendations."
    ),
    version="1.0.0",
    lifespan=lifespan,
)


# ──────────────────────────────────────────────
# CORS Middleware
# ──────────────────────────────────────────────

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# ──────────────────────────────────────────────
# Routes
# ──────────────────────────────────────────────

app.include_router(calls_router)
app.include_router(dashboard_router)


@app.get("/", tags=["Health"])
async def root():
    """API root — health check."""
    return {
        "service": "CallSense API",
        "version": "1.0.0",
        "status": "healthy",
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health_check():
    """Detailed health check."""
    settings = get_settings()
    return {
        "status": "healthy",
        "environment": settings.APP_ENV,
        "models": {
            "primary": settings.GPT_MODEL_PRIMARY,
            "secondary": settings.GPT_MODEL_SECONDARY,
            "whisper": settings.WHISPER_MODEL,
        },
    }


# ──────────────────────────────────────────────
# Entry Point
# ──────────────────────────────────────────────

if __name__ == "__main__":
    import uvicorn

    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.APP_HOST,
        port=settings.APP_PORT,
        reload=settings.APP_DEBUG,
    )
