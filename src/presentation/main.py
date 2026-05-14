"""FastAPI application entry point.

This module initializes the FastAPI application with lifespan management,
routers, middleware, and observability setup.
"""

from collections.abc import AsyncIterator
from contextlib import asynccontextmanager

import structlog
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from configuration.dependencies import get_app_version, get_settings
from observability.logging import setup_logging
from observability.metrics import setup_metrics
from presentation.api.middleware.auth import register_auth_middleware
from presentation.api.middleware.error_handler import register_exception_handlers
from presentation.api.middleware.request_logging import register_logging_middleware
from presentation.api.v1.routers.health import include_health_router
from presentation.api.v1.routers.index import include_index_router


log = structlog.get_logger(__name__)

# Load settings at startup (with validation)
settings = get_settings()

_VERSION = get_app_version(settings.app.name)


@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncIterator[None]:
    """Manage application startup and shutdown lifecycle."""
    setup_logging()
    log.info("application.started", version=_VERSION)
    yield
    log.info("application.stopped", version=_VERSION)


app = FastAPI(
    title=settings.app.name,
    description=f"{settings.app.name}",
    version=_VERSION,
    lifespan=lifespan,
)

# Middleware (registered in reverse order of execution)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_logging_middleware(app)
register_auth_middleware(app)
register_exception_handlers(app)

# Routers
include_health_router(app)
include_index_router(app)

# Metrics instrumentation (must be after middleware registration, before app starts)
try:
    setup_metrics(app)
except Exception:
    log.warning("metrics.setup_failed", exc_info=True)
