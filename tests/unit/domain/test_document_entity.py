"""Tests for the Document domain entity."""

from uuid import UUID

import pytest

from domain.entities.document import Document


class TestDocumentEntity:
    """Verify the Document entity follows clean architecture rules."""

    def test_document_creation(self) -> None:
        doc = Document(title="Test Doc", source_path="/tmp/test.pdf")
        assert doc.title == "Test Doc"
        assert doc.source_path == "/tmp/test.pdf"

    def test_document_has_unique_id(self) -> None:
        doc1 = Document(title="Doc 1", source_path="/a.pdf")
        doc2 = Document(title="Doc 2", source_path="/b.pdf")
        assert isinstance(doc1.id, UUID)
        assert doc1.id != doc2.id

    def test_document_no_external_dependencies(self) -> None:
        """Verify the entity module has only stdlib imports."""
        import ast
        import sys

        import domain.entities.document as doc_module

        source = doc_module.__file__ or ""
        with open(source) as f:
            tree = ast.parse(f.read())

        stdlib = sys.stdlib_module_names

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top in stdlib, f"Domain entity imports non-stdlib: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                assert top in stdlib, f"Domain entity imports non-stdlib: {node.module}"

    def test_document_rejects_empty_title(self) -> None:
        with pytest.raises(ValueError, match="title must not be empty"):
            Document(title="", source_path="/tmp/test.pdf")

    def test_document_rejects_empty_source_path(self) -> None:
        with pytest.raises(ValueError, match="source_path must not be empty"):
            Document(title="Test Doc", source_path="")
