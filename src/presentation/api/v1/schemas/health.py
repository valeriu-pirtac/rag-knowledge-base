"""Health check response schemas."""

from __future__ import annotations

from presentation.api.dto.base import CamelCaseModel


class HealthResponse(CamelCaseModel):
    """Health check response with system status."""

    status: str
    app: str
    environment: str
    metrics_enabled: bool
    version: str
