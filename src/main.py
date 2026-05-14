"""Application entry point.

Re-exports the FastAPI app from the presentation layer for use with
ASGI servers (uvicorn, gunicorn, etc.).
"""

from presentation.main import app


__all__ = ["app"]
