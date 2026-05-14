"""Unit tests for base DTO camelCase serialization."""

from __future__ import annotations

import pytest
from pydantic import Field

from presentation.api.dto.base import CamelCaseModel


class SampleModel(CamelCaseModel):
    first_name: str = Field(..., description="Test field")
    last_name: str = Field(..., description="Test field")


@pytest.mark.unit
class TestCamelCaseModel:
    """Tests for CamelCaseModel alias generation."""

    def test_serializes_to_camel_case(self) -> None:
        obj = SampleModel(first_name="John", last_name="Doe")
        data = obj.model_dump(by_alias=True)
        assert "firstName" in data
        assert "lastName" in data
        assert "first_name" not in data
        assert "last_name" not in data

    def test_populates_by_name(self) -> None:
        obj = SampleModel(first_name="Jane", last_name="Smith")
        assert obj.first_name == "Jane"
        assert obj.last_name == "Smith"
