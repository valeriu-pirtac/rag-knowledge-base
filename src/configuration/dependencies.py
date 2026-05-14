"""Dependency injection wiring.

This module exposes FastAPI-compatible dependency functions that resolve
concrete infrastructure implementations for each domain protocol.

Usage:
    from configuration.dependencies import get_settings

    @router.get("/example")
    async def example(settings: Annotated[AppSettings, Depends(get_settings)]) -> dict:
        ...
"""

import importlib.metadata
from functools import lru_cache

from configuration.settings import AppSettings


@lru_cache(maxsize=1)
def get_settings() -> AppSettings:
    """Get singleton settings instance.

    Uses functools.lru_cache to ensure settings are loaded only once
    and the same instance is returned on subsequent calls.

    Returns:
        Singleton AppSettings instance

    Raises:
        ValidationError: If required settings are missing or invalid
    """
    return AppSettings()


def get_app_version(app_name: str) -> str:
    """Resolve the installed package version, falling back to 'unknown'."""
    try:
        return importlib.metadata.version(app_name)
    except importlib.metadata.PackageNotFoundError:
        return "unknown"


# Add repository / service dependencies here, e.g.:
#
# from domain.protocols.item_repository import ItemRepository
# from infrastructure.in_memory.item_repository import InMemoryItemRepository
#
# def get_item_repository() -> ItemRepository:
#     return InMemoryItemRepository()
