"""Base DTO with camelCase alias generation.

All API response models should extend this base to ensure consistent
camelCase JSON field naming as specified in the architecture conventions.
"""

from __future__ import annotations

from pydantic import AliasGenerator, BaseModel
from pydantic.alias_generators import to_camel


class CamelCaseModel(BaseModel):
    """Base model with automatic camelCase alias generation for JSON fields."""

    model_config = {
        "alias_generator": AliasGenerator(
            serialization_alias=to_camel,
        ),
        "populate_by_name": True,
        "from_attributes": True,
    }
