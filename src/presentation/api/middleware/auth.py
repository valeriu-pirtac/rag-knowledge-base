"""JWT authentication middleware.

Provides stateless JWT token validation using PyJWT.
For MVP, uses a single shared secret via JWT_SECRET environment variable.
"""

from __future__ import annotations

from collections.abc import Awaitable, Callable

import jwt
import structlog
from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from configuration.dependencies import get_settings


log = structlog.get_logger(__name__)


class JWTAuthMiddleware(BaseHTTPMiddleware):
    """Middleware that validates JWT tokens on protected routes.

    Skips validation for:
      - /v1/health
      - /v1/
      - /docs, /openapi.json, /redoc
      - /metrics
    """

    SKIP_PATHS = frozenset(
        {
            "/v1/health",
            "/v1/health/",
            "/v1/",
            "/docs",
            "/docs/",
            "/openapi.json",
            "/redoc",
            "/metrics",
            "/metrics/",
        }
    )

    async def dispatch(self, request: Request, call_next: Callable[[Request], Awaitable[Response]]) -> Response:
        if request.url.path in self.SKIP_PATHS:
            return await call_next(request)

        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            log.warning("auth.missing_token", path=request.url.path)
            return JSONResponse(status_code=401, content={"detail": "Missing or invalid Authorization header"})

        token = auth_header.removeprefix("Bearer ")
        settings = get_settings()

        try:
            jwt.decode(token, settings.jwt.secret, algorithms=[settings.jwt.algorithm])
        except jwt.ExpiredSignatureError:
            log.warning("auth.token_expired", path=request.url.path)
            return JSONResponse(status_code=401, content={"detail": "Token has expired"})
        except jwt.InvalidTokenError as exc:
            log.warning("auth.token_invalid", path=request.url.path, error=str(exc))
            return JSONResponse(status_code=401, content={"detail": "Invalid token"})

        return await call_next(request)


def register_auth_middleware(app: FastAPI) -> None:
    """Register JWT auth middleware on the FastAPI app."""
    app.add_middleware(JWTAuthMiddleware)
