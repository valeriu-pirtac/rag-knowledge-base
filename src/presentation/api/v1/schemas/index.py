"""Index root endpoint response schemas."""

from __future__ import annotations

from presentation.api.dto.base import CamelCaseModel


class IndexResponse(CamelCaseModel):
    """Root endpoint response with service identity."""

    service: str
    status: str
    version: str
