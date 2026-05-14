"""Application metadata configuration."""

from pydantic import BaseModel, Field


class AppConfig(BaseModel):
    """Application metadata configuration."""

    name: str = Field(default="rag-knowledge-base", description="Application name")
    env: str = Field(default="dev", description="Application environment (e.g. dev, staging, prod)")
