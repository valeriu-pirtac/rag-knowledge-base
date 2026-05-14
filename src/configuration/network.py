"""Docker network configuration."""

from pydantic import BaseModel, Field


class NetworkConfig(BaseModel):
    """Docker network configuration."""

    name: str = Field(default="rag_network", description="Docker network name")
