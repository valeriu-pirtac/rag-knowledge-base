"""Cache configuration — Redis.

Mirrors docker-compose.cache.yaml.
"""

from pydantic import BaseModel, Field


class RedisConfig(BaseModel):
    """Redis cache configuration."""

    port: int = Field(default=6379, ge=1, le=65535, description="Redis port")
