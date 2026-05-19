"""
Dashboard Router — provides aggregated statistics and analytics.
"""

import logging
from fastapi import APIRouter

from app.models.schemas import DashboardStats
from app.services.supabase_service import get_supabase_service

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/dashboard", tags=["Dashboard"])


@router.get("/stats", response_model=DashboardStats)
async def get_dashboard_stats():
    """Get aggregated dashboard statistics."""
    db = get_supabase_service()
    stats = db.get_dashboard_stats()

    return DashboardStats(
        total_calls=stats.get("total_calls", 0),
        avg_quality_score=stats.get("avg_quality_score"),
        avg_resolution_rate=stats.get("avg_resolution_rate"),
        sentiment_distribution=stats.get("sentiment_distribution", {}),
        category_distribution=stats.get("category_distribution", {}),
        urgency_distribution=stats.get("urgency_distribution", {}),
        recent_calls=stats.get("recent_calls", []),
    )
