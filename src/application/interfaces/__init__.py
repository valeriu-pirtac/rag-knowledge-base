"""Application interfaces - Adapter protocols."""

from .document_repository import DocumentRepositoryInterface
from .storage import StorageInterface


__all__: list[str] = [
    "DocumentRepositoryInterface",
    "StorageInterface",
]
