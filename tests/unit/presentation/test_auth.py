"""Unit tests for JWT authentication middleware."""

from __future__ import annotations

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from configuration.dependencies import get_settings


@pytest.mark.unit
class TestJWTAuthMiddleware:
    """Tests for JWT authentication on protected routes."""

    def test_health_returns_200_without_token(self, client: TestClient) -> None:
        response = client.get("/v1/health")
        assert response.status_code == 200

    def test_public_routes_accessible_without_token(self, client: TestClient) -> None:
        routes = ["/v1/", "/v1/health", "/docs", "/openapi.json", "/metrics"]
        for route in routes:
            response = client.get(route)
            assert response.status_code != 401, f"Route {route} should not require auth"

    def test_protected_route_rejects_missing_header(self, client: TestClient) -> None:
        response = client.get("/v1/nonexistent")
        assert response.status_code == 401

    def test_protected_route_rejects_invalid_token(self, client: TestClient) -> None:
        response = client.get("/v1/nonexistent", headers={"Authorization": "Bearer invalidtoken"})
        assert response.status_code == 401
        assert "detail" in response.json()

    def test_protected_route_accepts_valid_token(self, client: TestClient) -> None:
        settings = get_settings()
        token = pyjwt.encode({"sub": "test-user"}, settings.jwt.secret, algorithm=settings.jwt.algorithm)
        response = client.get("/v1/nonexistent", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404  # Not found, but auth passed

    def test_protected_route_rejects_expired_token(self, client: TestClient) -> None:
        settings = get_settings()
        import time

        expired = pyjwt.encode(
            {"sub": "test-user", "exp": int(time.time()) - 3600},
            settings.jwt.secret,
            algorithm=settings.jwt.algorithm,
        )
        response = client.get("/v1/nonexistent", headers={"Authorization": f"Bearer {expired}"})
        assert response.status_code == 401
        assert "detail" in response.json()
