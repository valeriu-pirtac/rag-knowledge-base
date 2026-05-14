"""Storage configuration — PostgreSQL and Garage S3.

Mirrors docker-compose.storage.yaml.
"""

from pydantic import BaseModel, Field


class PostgresConfig(BaseModel):
    """PostgreSQL database configuration."""

    user: str = Field(default="rag_user", description="PostgreSQL user")
    password: str = Field(default="rag_pass", description="PostgreSQL password")
    db: str = Field(default="rag_knowledge_base", description="PostgreSQL database name")
    port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")


class GarageConfig(BaseModel):
    """Garage S3-compatible storage configuration."""

    s3_port: int = Field(default=3900, ge=1, le=65535, description="Garage S3 API port")
    web_port: int = Field(default=3901, ge=1, le=65535, description="Garage web interface port")
    rpc_port: int = Field(default=3902, ge=1, le=65535, description="Garage RPC port")
    admin_port: int = Field(default=3903, ge=1, le=65535, description="Garage admin port")
    rpc_secret: str = Field(default="", description="Garage RPC secret key")
    log_level: str = Field(default="garage=info", description="Garage log level")
