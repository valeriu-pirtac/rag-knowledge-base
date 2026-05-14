"""Application configuration management with Pydantic Settings.

Aggregates all domain-specific config classes into a single AppSettings
model loaded from environment variables / .env file.
"""

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

from configuration.app import AppConfig
from configuration.cache import RedisConfig
from configuration.messaging import NatsConfig
from configuration.network import NetworkConfig
from configuration.observability import LogConfig, MetricsConfig
from configuration.security import JWTConfig
from configuration.server import ServerConfig
from configuration.storage import GarageConfig, PostgresConfig


class BaseAppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_nested_delimiter="_",
        case_sensitive=False,
        extra="ignore",
    )


class AppSettings(BaseAppSettings):
    """Application configuration with validation.

    All settings are loaded from environment variables or .env file.
    Required fields will raise ValidationError on startup if missing.
    """

    app: AppConfig = Field(default_factory=AppConfig, description="Application metadata")
    log: LogConfig = Field(default_factory=LogConfig, description="Structured logging settings")
    metrics: MetricsConfig = Field(default_factory=MetricsConfig, description="Prometheus metrics settings")
    jwt: JWTConfig = Field(default_factory=JWTConfig, description="JWT authentication settings")
    server: ServerConfig = Field(default_factory=ServerConfig, description="Server bind settings")
    network: NetworkConfig = Field(default_factory=NetworkConfig, description="Docker network settings")
    postgres: PostgresConfig = Field(default_factory=PostgresConfig, description="PostgreSQL database settings")
    redis: RedisConfig = Field(default_factory=RedisConfig, description="Redis cache settings")
    nats: NatsConfig = Field(default_factory=NatsConfig, description="NATS messaging settings")
    garage: GarageConfig = Field(default_factory=GarageConfig, description="Garage S3 storage settings")
