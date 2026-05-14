"""Repository interface for Document persistence."""

from abc import ABC, abstractmethod
from uuid import UUID

from domain.entities.document import Document
from domain.value_objects.document_status import DocumentStatus


class DocumentRepositoryInterface(ABC):
    """Abstract interface for document storage operations."""

    @abstractmethod
    async def save(self, document: Document) -> Document:
        """Persist a new document and return it with generated fields."""

    @abstractmethod
    async def exists_by_checksum_and_workspace(self, checksum: str, workspace_id: UUID) -> bool:
        """Check if a document with the given checksum exists in the workspace."""

    @abstractmethod
    async def find_by_checksum_and_workspace(self, checksum: str, workspace_id: UUID) -> Document | None:
        """Find a document by checksum scoped to a workspace."""

    @abstractmethod
    async def find_by_id(self, document_id: UUID) -> Document | None:
        """Retrieve a document by its unique identifier."""

    @abstractmethod
    async def update_status(self, document_id: UUID, status: DocumentStatus, error_message: str | None = None) -> None:
        """Update the processing status of a document."""
