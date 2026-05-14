"""Messaging configuration — NATS.

Mirrors docker-compose.messaging.yaml.
"""

from pydantic import BaseModel, Field


class NatsConfig(BaseModel):
    """NATS messaging configuration."""

    client_port: int = Field(default=4222, ge=1, le=65535, description="NATS client port")
    http_port: int = Field(default=8222, ge=1, le=65535, description="NATS HTTP monitoring port")
