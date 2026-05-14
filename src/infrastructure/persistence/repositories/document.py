"""SQLAlchemy implementation of DocumentRepositoryInterface."""

from uuid import UUID

from sqlalchemy import exists, select
from sqlalchemy.ext.asyncio import AsyncSession

from application.interfaces import DocumentRepositoryInterface
from domain.entities.document import Document
from domain.value_objects.document_status import DocumentStatus
from infrastructure.persistence.models import DocumentModel


class DocumentRepository(DocumentRepositoryInterface):
    """Repository for Document entities using SQLAlchemy."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def save(self, document: Document) -> Document:
        model = DocumentModel(
            document_id=document.document_id,
            workspace_id=document.workspace_id,
            checksum=document.checksum,
            size=document.size,
            status=document.status.value,
            error_message=document.error_message,
            s3_storage_path=document.s3_storage_path,
            mime_type=document.mime_type,
        )
        self._session.add(model)
        await self._session.flush()
        return self._to_domain(model)

    async def exists_by_checksum_and_workspace(self, checksum: str, workspace_id: UUID) -> bool:
        stmt = exists(
            select(DocumentModel).where(
                DocumentModel.checksum == checksum,
                DocumentModel.workspace_id == workspace_id,
            )
        ).select()
        result = await self._session.execute(stmt)
        return result.scalar() or False

    async def find_by_checksum_and_workspace(self, checksum: str, workspace_id: UUID) -> Document | None:
        stmt = select(DocumentModel).where(
            DocumentModel.checksum == checksum,
            DocumentModel.workspace_id == workspace_id,
        )
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def find_by_id(self, document_id: UUID) -> Document | None:
        stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        return self._to_domain(model) if model else None

    async def update_status(self, document_id: UUID, status: DocumentStatus, error_message: str | None = None) -> None:
        stmt = select(DocumentModel).where(DocumentModel.document_id == document_id)
        result = await self._session.execute(stmt)
        model = result.scalar_one_or_none()
        if model:
            model.status = status.value
            model.error_message = error_message

    @staticmethod
    def _to_domain(model: DocumentModel) -> Document:
        return Document(
            document_id=model.document_id,
            workspace_id=model.workspace_id,
            checksum=model.checksum,
            size=model.size,
            status=DocumentStatus(model.status),
            error_message=model.error_message,
            s3_storage_path=model.s3_storage_path,
            mime_type=model.mime_type,
            created_at=model.created_at,
            updated_at=model.updated_at,
        )
