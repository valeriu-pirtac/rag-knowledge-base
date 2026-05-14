"""Documents router — streaming upload endpoint."""

import uuid
from collections.abc import AsyncIterator
from http import HTTPStatus
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, FastAPI, Header, Request
from fastapi.responses import JSONResponse

from application.use_cases.ingestion.upload_document import UploadDocumentUseCase
from configuration.dependencies import get_session_factory, get_settings
from configuration.settings import AppSettings
from domain.exceptions import DuplicateEntityError
from domain.value_objects.document_status import DocumentStatus
from infrastructure.adapters.s3_adapter import S3StorageAdapter
from infrastructure.persistence.repositories import DocumentRepository
from presentation.api.v1.schemas.document import UploadDocumentResponse


router = APIRouter(prefix="/v1", tags=["documents"])


@router.post("/documents/{workspace_id}", status_code=HTTPStatus.CREATED)
async def upload_document(
    workspace_id: UUID,
    request: Request,
    content_type: Annotated[str, Header()],
    content_length: Annotated[int, Header()],
    settings: Annotated[AppSettings, Depends(get_settings)],
) -> JSONResponse:
    total_size = content_length
    if total_size <= 0:
        return JSONResponse(
            status_code=HTTPStatus.BAD_REQUEST,
            content=UploadDocumentResponse(
                document_id="",
                status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                error_message=f"Invalid Content-Length: '{content_length}'",
            ).model_dump(),
        )

    if total_size > settings.ingestion.max_document_size:
        return JSONResponse(
            status_code=HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
            content=UploadDocumentResponse(
                document_id="",
                status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                error_message=(
                    f"File size {content_length} bytes exceeds maximum"
                    f" allowed {settings.ingestion.max_document_size} bytes"
                ),
            ).model_dump(),
        )

    mime_type = content_type.lower().strip()
    if mime_type not in settings.ingestion.accepted_mime_types:
        return JSONResponse(
            status_code=HTTPStatus.UNSUPPORTED_MEDIA_TYPE,
            content=UploadDocumentResponse(
                document_id="",
                status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                error_message=f"Unsupported media type '{content_type}'",
            ).model_dump(),
        )

    async def stream_chunks() -> AsyncIterator[bytes]:
        async for chunk in request.stream():
            yield chunk

    factory = get_session_factory()
    async with factory() as session:
        try:
            repo = DocumentRepository(session)
            storage = S3StorageAdapter(settings.garage)
            use_case = UploadDocumentUseCase(repo, storage, settings.ingestion)

            document_id = uuid.uuid4()

            await use_case.execute(document_id, workspace_id, mime_type, total_size, stream_chunks())
            await session.commit()

            doc = await repo.find_by_id(document_id)
            if doc is None:
                return JSONResponse(
                    status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                    content=UploadDocumentResponse(
                        document_id="",
                        status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                        error_message="Document not found after upload",
                    ).model_dump(),
                )
            return JSONResponse(
                status_code=HTTPStatus.CREATED,
                content=UploadDocumentResponse(
                    document_id=str(doc.document_id),
                    checksum=doc.checksum,
                    size=doc.size,
                    mime_type=doc.mime_type,
                    status=doc.status.value,
                ).model_dump(),
            )
        except DuplicateEntityError as exc:
            return JSONResponse(
                status_code=HTTPStatus.CONFLICT,
                content=UploadDocumentResponse(
                    document_id="",
                    status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                    error_message=str(exc),
                ).model_dump(),
            )
        except Exception as exc:
            await session.rollback()
            return JSONResponse(
                status_code=HTTPStatus.INTERNAL_SERVER_ERROR,
                content=UploadDocumentResponse(
                    document_id="",
                    status=DocumentStatus.FILE_UPLOAD_FAILED.value,
                    error_message=str(exc),
                ).model_dump(),
            )


def include_documents_router(app: FastAPI) -> None:
    """Register the documents router on the FastAPI app."""
    app.include_router(router)
