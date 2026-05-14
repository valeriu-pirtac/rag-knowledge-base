"""Health router."""

from __future__ import annotations

from typing import Annotated

import structlog
from fastapi import APIRouter, Depends, FastAPI

from configuration.dependencies import get_app_version, get_settings
from configuration.settings import AppSettings
from presentation.api.v1.schemas import HealthResponse


log = structlog.get_logger(__name__)

router = APIRouter(prefix="/v1", tags=["health"])


@router.get("/health", response_model=HealthResponse, response_model_by_alias=True)
async def health(settings: Annotated[AppSettings, Depends(get_settings)]) -> HealthResponse:
    """Health check endpoint returning system status."""
    version = get_app_version(settings.app.name)
    return HealthResponse(
        status="healthy",
        app=settings.app.name,
        environment=settings.app.env,
        metrics_enabled=settings.metrics.enabled,
        version=version,
    )


def include_health_router(app: FastAPI) -> None:
    """Register the health router on the FastAPI app."""
    app.include_router(router)
