"""Storage configuration — PostgreSQL, Garage S3, and ingestion settings."""

from pydantic import BaseModel, Field, SecretStr


class DatabaseConfig(BaseModel):
    """PostgreSQL database configuration."""

    user: str = Field(default="rag_user", description="PostgreSQL user")
    password: SecretStr = Field(default=SecretStr("rag_pass"), description="PostgreSQL password")
    db: str = Field(default="rag_knowledge_base", description="PostgreSQL database name")
    host: str = Field(default="localhost", description="PostgreSQL host")
    port: int = Field(default=5432, ge=1, le=65535, description="PostgreSQL port")


class StorageConfig(BaseModel):
    """Garage S3-compatible storage configuration."""

    host: str = Field(default="garage", description="Garage S3 hostname")
    protocol: str = Field(default="http", description="Garage S3 protocol (http or https)")
    s3_port: int = Field(default=3900, ge=1, le=65535, description="Garage S3 API port")
    web_port: int = Field(default=3901, ge=1, le=65535, description="Garage web interface port")
    rpc_port: int = Field(default=3902, ge=1, le=65535, description="Garage RPC port")
    admin_port: int = Field(default=3903, ge=1, le=65535, description="Garage admin port")
    access_key_secret: SecretStr = Field(default=SecretStr(""), description="Garage S3 access key secret")
    access_key_id: str = Field(default="root", description="Garage S3 access key ID")
    bucket_name: str = Field(default="rag-knowledge-base", description="Garage S3 bucket name")
    timeout: int = Field(default=5, ge=1, description="S3 client timeout in seconds")
    log_level: str = Field(default="garage=info", description="Garage log level")


class IngestionConfig(BaseModel):
    """Document ingestion configuration."""

    max_document_size: int = Field(
        default=104_857_600,  # 100 MB
        ge=1,
        description="Maximum allowed document size in bytes",
    )
    accepted_mime_types: list[str] = Field(
        default=["application/pdf"],
        description="List of accepted MIME types for upload",
    )
