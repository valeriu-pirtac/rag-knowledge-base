"""Upload document response schema."""

from pydantic import BaseModel


class UploadDocumentResponse(BaseModel):
    document_id: str
    checksum: str | None = None
    size: int | None = None
    mime_type: str | None = None
    status: str
    error_message: str | None = None
