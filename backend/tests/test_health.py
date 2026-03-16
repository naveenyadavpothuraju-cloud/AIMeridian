"""Tests for the health check endpoint."""

from fastapi.testclient import TestClient

from app.main import app

client = TestClient(app)


def test_health_check_returns_200() -> None:
    """Health endpoint must return 200 with status ok."""
    response = client.get("/health")
    assert response.status_code == 200


def test_health_check_response_shape() -> None:
    """Health endpoint must return status and version keys."""
    response = client.get("/health")
    body = response.json()
    assert body["status"] == "ok"
    assert "version" in body
