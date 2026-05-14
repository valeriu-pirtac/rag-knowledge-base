"""Dependency injection wiring.

This module exposes FastAPI-compatible dependency functions that resolve
concrete infrastructure implementations for each domain protocol.
"""

import importlib.metadata
from collections.abc import AsyncIterator
from functools import lru_cache

from sqlalchemy.ext.asyncio import AsyncEngine, AsyncSession, async_sessionmaker, create_async_engine

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


@lru_cache(maxsize=1)
def create_engine() -> AsyncEngine:
    """Create an async SQLAlchemy engine from DatabaseConfig. Singleton per app."""
    postgres = get_settings().postgres
    dsn = (
        f"postgresql+asyncpg://{postgres.user}:{postgres.password.get_secret_value()}"
        f"@{postgres.host}:{postgres.port}/{postgres.db}"
    )
    return create_async_engine(dsn, echo=False, pool_pre_ping=True)


def get_session_factory() -> async_sessionmaker[AsyncSession]:
    """Return the singleton session factory."""
    return async_sessionmaker(create_engine(), class_=AsyncSession, expire_on_commit=False)


async def get_session() -> AsyncIterator[AsyncSession]:
    """Yield an async database session with automatic commit/rollback.

    Commits on success, rolls back on exception.
    """
    factory = get_session_factory()
    async with factory() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            pass  # engine is long-lived, don't dispose
