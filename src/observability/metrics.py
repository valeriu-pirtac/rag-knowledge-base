"""Prometheus metrics configuration.

Sets up prometheus-fastapi-instrumentator to expose a /metrics endpoint
and registers application-level custom metrics.
"""

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator

from configuration.dependencies import get_settings


def setup_metrics(app: FastAPI) -> None:
    """Configure Prometheus metrics and expose /metrics endpoint.

    Must be called BEFORE the application starts (i.e. at module level,
    not in a lifespan handler) because the instrumentator registers
    middleware internally.
    """
    settings = get_settings()
    if not settings.metrics.enabled:
        return

    Instrumentator().instrument(app).expose(app)
