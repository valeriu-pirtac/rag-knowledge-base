"""Unit tests for global HTTP exception handlers."""

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from configuration.dependencies import get_settings


@pytest.mark.unit
class TestErrorHandlers:
    """Test that unknown paths return 404."""

    def test_unknown_path_returns_404(self, client: TestClient) -> None:
        """Verify that requests to unknown paths return HTTP 404."""
        settings = get_settings()
        token = pyjwt.encode({"sub": "test"}, settings.jwt.secret, algorithm=settings.jwt.algorithm)
        response = client.get("/v1/nonexistent-path", headers={"Authorization": f"Bearer {token}"})
        assert response.status_code == 404
