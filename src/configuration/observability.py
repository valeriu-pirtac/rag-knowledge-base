"""Observability configuration — logging and metrics."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class LogConfig(BaseModel):
    """Structured logging configuration."""

    level: str = Field(default="INFO", description="Logging level")
    format: Literal["json", "console"] = Field(default="json", description="Log format")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        valid_levels = {"DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"}
        v_upper = v.upper()
        if v_upper not in valid_levels:
            raise ValueError(f"Log level must be one of: {', '.join(valid_levels)}")
        return v_upper


class MetricsConfig(BaseModel):
    """Prometheus metrics configuration."""

    enabled: bool = Field(default=True, description="Enable Prometheus metrics")
