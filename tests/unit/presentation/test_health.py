"""Unit tests for the health endpoint."""

import pytest
from fastapi.testclient import TestClient


@pytest.mark.unit
class TestHealthEndpoint:
    """Tests for GET /v1/health."""

    def test_health_returns_200(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_health_returns_system_status(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        data = response.json()
        assert data["status"] == "healthy"
        assert data["app"] == "rag-knowledge-base"
        assert "environment" in data
        assert "metricsEnabled" in data
        assert "version" in data
