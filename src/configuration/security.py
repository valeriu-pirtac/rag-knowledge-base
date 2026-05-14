"""Security configuration — JWT authentication."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class JWTConfig(BaseModel):
    """JWT authentication configuration."""

    secret: str = Field(default="dev-secret-do-not-use-in-production", description="JWT signing secret")
    algorithm: Literal["HS256", "RS256"] = Field(default="HS256", description="JWT signing algorithm")

    @field_validator("algorithm")
    @classmethod
    def validate_algorithm(cls, v: str) -> str:
        if v == "RS256":
            raise ValueError("RS256 algorithm is not supported at the moment, use only HS256")
        return v
