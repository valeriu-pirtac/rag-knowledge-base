"""Document entity - core domain entity for uploaded documents."""

from dataclasses import dataclass, field
from datetime import UTC, datetime
from uuid import UUID, uuid4

from domain.value_objects.document_status import DocumentStatus


@dataclass
class Document:
    """A domain entity representing an ingested document."""

    workspace_id: UUID
    checksum: str | None = None
    size: int | None = None
    mime_type: str | None = None
    status: DocumentStatus = DocumentStatus.FILE_UPLOAD_PENDING
    error_message: str | None = None
    s3_storage_path: str | None = None
    document_id: UUID = field(default_factory=uuid4)
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
