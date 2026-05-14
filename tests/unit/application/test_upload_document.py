"""Unit tests for the UploadDocumentUseCase."""

import hashlib
from unittest.mock import AsyncMock
from uuid import UUID, uuid4

import pytest

from application.interfaces import DocumentRepositoryInterface, StorageInterface
from application.use_cases.ingestion.upload_document import UploadDocumentUseCase
from configuration.storage import IngestionConfig
from domain.entities.document import Document
from domain.exceptions import DuplicateEntityError
from domain.value_objects.document_status import DocumentStatus


WS1 = UUID("00000000-0000-0000-0000-000000000001")
WS2 = UUID("00000000-0000-0000-0000-000000000002")

MIME = "application/pdf"


@pytest.fixture
def mock_repo() -> AsyncMock:
    return AsyncMock(spec=DocumentRepositoryInterface)


@pytest.fixture
def mock_storage() -> AsyncMock:
    return AsyncMock(spec=StorageInterface)


@pytest.fixture
def config() -> IngestionConfig:
    return IngestionConfig(max_document_size=10_485_760)


@pytest.fixture
def use_case(
    mock_repo: AsyncMock,
    mock_storage: AsyncMock,
    config: IngestionConfig,
) -> UploadDocumentUseCase:
    return UploadDocumentUseCase(repository=mock_repo, storage=mock_storage, config=config)


@pytest.mark.unit
class TestUploadDocumentUseCase:
    """Tests for the document upload use case."""

    @pytest.mark.asyncio
    async def test_upload_success(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        content = b"fake pdf content"
        checksum = hashlib.sha256(content).hexdigest()
        document_id = uuid4()
        mock_repo.find_by_checksum_and_workspace.return_value = None
        mock_repo.save.return_value = None
        mock_storage.build_key.return_value = f"bronze/{WS1}/raw_documents/pdf/{document_id}"

        async def stream():
            yield content

        await use_case.execute(document_id, WS1, MIME, len(content), stream())

        mock_repo.find_by_checksum_and_workspace.assert_awaited_once_with(checksum, WS1)
        mock_repo.save.assert_awaited_once()
        mock_storage.store_stream.assert_awaited_once()
        mock_repo.update_status.assert_awaited_once_with(document_id, DocumentStatus.FILE_UPLOAD_COMPLETED)

    @pytest.mark.asyncio
    async def test_upload_duplicate_detected(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        content = b"duplicate content"
        checksum = hashlib.sha256(content).hexdigest()
        existing_doc = Document(
            workspace_id=WS1,
            checksum=checksum,
            size=len(content),
            status=DocumentStatus.FILE_UPLOAD_COMPLETED,
        )
        mock_repo.find_by_checksum_and_workspace.return_value = existing_doc

        async def stream():
            yield content

        document_id = uuid4()
        with pytest.raises(DuplicateEntityError):
            await use_case.execute(document_id, WS1, MIME, len(content), stream())

        mock_storage.store_stream.assert_not_called()

    @pytest.mark.asyncio
    async def test_upload_empty_file(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        document_id = uuid4()
        mock_repo.find_by_checksum_and_workspace.return_value = None
        mock_repo.save.return_value = None

        async def stream():
            yield b""

        await use_case.execute(document_id, WS1, MIME, 0, stream())

        mock_repo.save.assert_awaited_once()
        mock_repo.update_status.assert_awaited_once_with(document_id, DocumentStatus.FILE_UPLOAD_COMPLETED)

    @pytest.mark.asyncio
    async def test_different_workspace_not_duplicate(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        content = b"same content different workspace"
        checksum = hashlib.sha256(content).hexdigest()

        existing_doc = Document(
            workspace_id=WS1,
            checksum=checksum,
            size=len(content),
            status=DocumentStatus.FILE_UPLOAD_COMPLETED,
        )

        def find_by_checksum_and_workspace(checksum_arg: str, workspace_id_arg: UUID) -> object:
            if workspace_id_arg == WS1:
                return existing_doc
            return None

        mock_repo.find_by_checksum_and_workspace.side_effect = find_by_checksum_and_workspace
        mock_repo.save.return_value = None

        async def stream():
            yield content

        document_id = uuid4()
        await use_case.execute(document_id, WS2, MIME, len(content), stream())

        mock_repo.save.assert_awaited_once()
        mock_repo.update_status.assert_awaited_once_with(document_id, DocumentStatus.FILE_UPLOAD_COMPLETED)

    @pytest.mark.asyncio
    async def test_streaming_chunks_accumulated(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
        mock_storage: AsyncMock,
    ) -> None:
        chunks = [b"chunk1", b"chunk2", b"chunk3"]
        combined = b"".join(chunks)
        mock_repo.find_by_checksum_and_workspace.return_value = None
        mock_repo.save.return_value = None

        async def stream():
            for c in chunks:
                yield c

        document_id = uuid4()
        await use_case.execute(document_id, WS1, MIME, len(combined), stream())

        mock_repo.save.assert_awaited_once()
        mock_repo.update_status.assert_awaited_once_with(document_id, DocumentStatus.FILE_UPLOAD_COMPLETED)

    @pytest.mark.asyncio
    async def test_repository_error_handling(
        self,
        use_case: UploadDocumentUseCase,
        mock_repo: AsyncMock,
    ) -> None:
        mock_repo.find_by_checksum_and_workspace.side_effect = Exception("DB error")

        async def stream():
            yield b"content"

        document_id = uuid4()
        with pytest.raises(Exception, match="DB error"):
            await use_case.execute(document_id, WS1, MIME, len(b"content"), stream())
