"""Upload document use case — streaming ingestion with deduplication."""

import hashlib
import tempfile
from collections.abc import AsyncIterator
from uuid import UUID

from application.interfaces import DocumentRepositoryInterface, StorageInterface
from configuration.storage import IngestionConfig
from domain.entities.document import Document
from domain.exceptions import DuplicateEntityError
from domain.value_objects.document_status import DocumentStatus


class UploadDocumentUseCase:
    """Orchestrate the streaming upload of a PDF document."""

    def __init__(
        self,
        repository: DocumentRepositoryInterface,
        storage: StorageInterface,
        config: IngestionConfig,
    ) -> None:
        self._repository = repository
        self._storage = storage
        self._config = config

    async def execute(
        self,
        document_id: UUID,
        workspace_id: UUID,
        mime_type: str | None,
        total_size: int,
        stream: AsyncIterator[bytes],
    ) -> None:

        sha256 = hashlib.sha256()
        with tempfile.SpooledTemporaryFile(max_size=10 * 1024 * 1024) as tmp:  # 10 MB in memory, then disk
            async for chunk in stream:
                sha256.update(chunk)
                tmp.write(chunk)

            checksum = sha256.hexdigest()

            existing = await self._repository.find_by_checksum_and_workspace(checksum, workspace_id)
            if existing is not None:
                raise DuplicateEntityError("Document Checksum", checksum)

            storage_key = self._storage.build_key(workspace_id, document_id, mime_type)

            doc = Document(
                document_id=document_id,
                workspace_id=workspace_id,
                checksum=checksum,
                size=total_size,
                status=DocumentStatus.FILE_UPLOAD_PENDING,
                s3_storage_path=storage_key,
                mime_type=mime_type,
            )
            await self._repository.save(doc)

            tmp.seek(0)

            async def file_chunks() -> AsyncIterator[bytes]:
                while chunk := tmp.read(8 * 1024 * 1024):
                    yield chunk

            await self._storage.store_stream(storage_key, file_chunks())

        await self._repository.update_status(document_id, DocumentStatus.FILE_UPLOAD_COMPLETED)
