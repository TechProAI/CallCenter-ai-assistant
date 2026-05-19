"""Tests for API endpoints."""

import pytest
from unittest.mock import patch, MagicMock


class TestHealthEndpoints:
    """Test health check endpoints."""

    def test_root(self, client):
        response = client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["service"] == "CallSense API"
        assert data["status"] == "healthy"

    def test_health_check(self, client):
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert "models" in data


class TestCallsEndpoints:
    """Test calls API endpoints."""

    @patch("app.routers.calls.get_supabase_service")
    def test_list_calls_empty(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.list_calls.return_value = ([], 0)
        mock_db.return_value = mock_service

        response = client.get("/api/calls/")
        assert response.status_code == 200
        data = response.json()
        assert data["total_count"] == 0
        assert data["calls"] == []

    @patch("app.routers.calls.get_supabase_service")
    def test_get_call_not_found(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.get_full_analysis.return_value = None
        mock_db.return_value = mock_service

        response = client.get("/api/calls/nonexistent_id")
        assert response.status_code == 404

    @patch("app.routers.calls.get_supabase_service")
    def test_get_status_not_found(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.get_call.return_value = None
        mock_db.return_value = mock_service

        response = client.get("/api/calls/status/nonexistent")
        assert response.status_code == 404

    @patch("app.routers.calls.get_supabase_service")
    def test_get_status_completed(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.get_call.return_value = {"call_id": "test_123", "status": "completed"}
        mock_db.return_value = mock_service

        response = client.get("/api/calls/status/test_123")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "completed"
        assert data["progress_percent"] == 100

    def test_analyze_transcript_too_short(self, client):
        response = client.post("/api/calls/analyze-transcript", json={"transcript": "too short"})
        assert response.status_code == 422  # Validation error

    @patch("app.routers.calls.run_analysis")
    @patch("app.routers.calls.get_supabase_service")
    def test_analyze_transcript_valid(self, mock_db, mock_run, client, sample_transcript):
        mock_service = MagicMock()
        mock_service.create_call.return_value = {"call_id": "test_123"}
        mock_db.return_value = mock_service

        response = client.post("/api/calls/analyze-transcript", json={"transcript": sample_transcript})
        assert response.status_code == 200
        data = response.json()
        assert "call_id" in data
        assert data["status"] == "processing"

    @patch("app.routers.calls.get_supabase_service")
    def test_delete_call_not_found(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.delete_call.return_value = False
        mock_db.return_value = mock_service

        response = client.delete("/api/calls/nonexistent")
        assert response.status_code == 404

    @patch("app.routers.calls.get_supabase_service")
    def test_delete_call_success(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.delete_call.return_value = True
        mock_db.return_value = mock_service

        response = client.delete("/api/calls/test_123")
        assert response.status_code == 200


class TestDashboardEndpoints:
    """Test dashboard endpoints."""

    @patch("app.routers.dashboard.get_supabase_service")
    def test_get_stats(self, mock_db, client):
        mock_service = MagicMock()
        mock_service.get_dashboard_stats.return_value = {
            "total_calls": 5,
            "avg_quality_score": 7.5,
            "avg_resolution_rate": 80.0,
            "sentiment_distribution": {"positive": 3, "neutral": 2},
            "category_distribution": {"technical_support": 3},
            "urgency_distribution": {"medium": 4},
            "recent_calls": [],
        }
        mock_db.return_value = mock_service

        response = client.get("/api/dashboard/stats")
        assert response.status_code == 200
        data = response.json()
        assert data["total_calls"] == 5
        assert data["avg_quality_score"] == 7.5
