"""Integration tests for the S3StorageAdapter."""

import uuid
from uuid import UUID

import pytest
import pytest_asyncio

from configuration.settings import AppSettings
from infrastructure.adapters.s3_adapter import S3StorageAdapter


WS1 = UUID("00000000-0000-0000-0000-000000000001")
DOC_ID = UUID("00000000-0000-0000-0000-0000000000aa")


@pytest.mark.integration
class TestS3StorageAdapter:
    """Tests S3StorageAdapter with a real Garbage S3 container."""

    @pytest_asyncio.fixture
    async def adapter(self) -> S3StorageAdapter:
        settings = AppSettings()
        adapter = S3StorageAdapter(settings.garage)
        adapter.ensure_bucket()
        return adapter

    @pytest.mark.asyncio
    async def test_store_and_retrieve(self, adapter: S3StorageAdapter) -> None:
        key = f"test/{uuid.uuid4()}.bin"
        data = b"hello s3 storage"
        stored_key = await adapter.store(key, data)
        assert stored_key == key

    @pytest.mark.asyncio
    async def test_store_stream(self, adapter: S3StorageAdapter) -> None:
        key = f"test/{uuid.uuid4()}.bin"

        async def stream():
            yield b"chunk1"
            yield b"chunk2"

        stored_key = await adapter.store_stream(key, stream())
        assert stored_key == key

    def test_build_key(self, adapter: S3StorageAdapter) -> None:
        key = adapter.build_key(WS1, DOC_ID, "application/pdf")
        assert (
            key == "bronze/00000000-0000-0000-0000-000000000001/raw_documents/pdf/00000000-0000-0000-0000-0000000000aa"
        )

    def test_build_key_unknown_mime(self, adapter: S3StorageAdapter) -> None:
        key = adapter.build_key(WS1, DOC_ID, "image/png")
        assert (
            key == "bronze/00000000-0000-0000-0000-000000000001/raw_documents/png/00000000-0000-0000-0000-0000000000aa"
        )

    def test_build_key_no_mime(self, adapter: S3StorageAdapter) -> None:
        key = adapter.build_key(WS1, DOC_ID, None)
        assert (
            key
            == "bronze/00000000-0000-0000-0000-000000000001/raw_documents/unknown/00000000-0000-0000-0000-0000000000aa"
        )
