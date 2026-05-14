"""Storage interface for file persistence."""

from abc import ABC, abstractmethod
from collections.abc import AsyncIterator
from uuid import UUID


class StorageInterface(ABC):
    """Abstract interface for object storage operations."""

    @abstractmethod
    async def store(self, key: str, data: bytes) -> str:
        """Store a blob of bytes and return the storage path."""

    @abstractmethod
    async def store_stream(self, key: str, stream: AsyncIterator[bytes]) -> str:
        """Store data from an async byte stream and return the storage path."""

    @abstractmethod
    def build_key(self, workspace_id: UUID, document_id: UUID, mime_type: str | None) -> str:
        """Build an object storage key for a document."""
