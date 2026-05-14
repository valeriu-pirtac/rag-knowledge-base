"""Document processing status enum."""

from enum import StrEnum


class DocumentStatus(StrEnum):
    """Represents the lifecycle status of a document."""

    FILE_UPLOAD_PENDING = "FILE_UPLOAD_PENDING"
    FILE_UPLOAD_IN_PROGRESS = "FILE_UPLOAD_IN_PROGRESS"
    FILE_UPLOAD_COMPLETED = "FILE_UPLOAD_COMPLETED"
    FILE_UPLOAD_FAILED = "FILE_UPLOAD_FAILED"
