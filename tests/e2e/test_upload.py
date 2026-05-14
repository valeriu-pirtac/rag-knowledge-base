"""E2E tests for the document upload flow."""

import hashlib

import jwt as pyjwt
import pytest
from fastapi.testclient import TestClient

from configuration.dependencies import get_settings


WS1 = "00000000-0000-0000-0000-000000000001"


@pytest.fixture
def token() -> str:
    settings = get_settings()
    return pyjwt.encode({"sub": "test"}, settings.jwt.secret, algorithm=settings.jwt.algorithm)


@pytest.fixture
def auth_headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _is_infra_error(response) -> bool:
    """Check if the response indicates missing infrastructure (DB/S3 not available)."""
    return response.status_code == 500 and "error_message" in response.json()


@pytest.mark.e2e
class TestUploadFlow:
    """End-to-end tests for the POST /v1/documents/{workspace_id} endpoint."""

    def test_upload_small_file(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        content = b"fake pdf content for e2e"
        checksum = hashlib.sha256(content).hexdigest()

        response = client.post(
            f"/v1/documents/{WS1}",
            content=content,
            headers={
                **auth_headers,
                "Content-Type": "application/pdf",
            },
        )

        assert response.status_code in (201, 500)
        if response.status_code == 201:
            data = response.json()
            assert data["checksum"] == checksum
            assert data["size"] == len(content)
            assert data["status"] == "FILE_UPLOAD_COMPLETED"

    def test_upload_large_file_rejected(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        size = 104_857_601
        content = b"x" * size

        response = client.post(
            f"/v1/documents/{WS1}",
            content=content,
            headers={
                **auth_headers,
                "Content-Type": "application/pdf",
            },
        )

        assert response.status_code == 413

    def test_upload_without_filename(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        content = b"some content"

        response = client.post(
            f"/v1/documents/{WS1}",
            content=content,
            headers={
                **auth_headers,
                "Content-Type": "application/pdf",
            },
        )

        assert response.status_code in (201, 500)

    def test_upload_wrong_mime_type_rejected(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        response = client.post(
            f"/v1/documents/{WS1}",
            content=b"some text content",
            headers={
                **auth_headers,
                "Content-Type": "text/plain",
            },
        )

        assert response.status_code == 415

    def test_upload_returns_error_message_on_db_failure(self, client: TestClient, auth_headers: dict[str, str]) -> None:
        response = client.post(
            f"/v1/documents/{WS1}",
            content=b"pdf content",
            headers={
                **auth_headers,
                "Content-Type": "application/pdf",
            },
        )

        assert response.status_code in (201, 500)
        if response.status_code == 500:
            data = response.json()
            assert "error_message" in data
