"""Index (root) router."""

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, FastAPI

from configuration.dependencies import get_app_version, get_settings
from configuration.settings import AppSettings
from presentation.api.v1.schemas import IndexResponse


log = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["index"])


@router.get("/", response_model=IndexResponse, response_model_by_alias=True)
async def root(app_settings: Annotated[AppSettings, Depends(get_settings)]) -> IndexResponse:
    """Root endpoint - returns service identity and version."""
    version = get_app_version(app_settings.app.name)
    return IndexResponse(
        service=app_settings.app.name,
        status="ok",
        version=version,
    )


def include_index_router(app: FastAPI) -> None:
    """Register the index router on the FastAPI app."""
    app.include_router(router)
