"""API v1 schemas - Pydantic request/response models."""

from presentation.api.v1.schemas.health import HealthResponse
from presentation.api.v1.schemas.index import IndexResponse


__all__ = ["HealthResponse", "IndexResponse"]
