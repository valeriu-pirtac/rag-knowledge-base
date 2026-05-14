"""Server bind configuration."""

from pydantic import BaseModel, Field


class ServerConfig(BaseModel):
    """Server bind configuration."""

    host: str = Field(default="0.0.0.0", description="Server bind host")
    port: int = Field(default=8000, ge=1, le=65535, description="Server bind port")
    workers: int = Field(default=1, gt=0, description="Number of worker processes")
