"""Tests for the Document domain entity."""

from uuid import UUID

from domain.entities.document import Document


WS1 = UUID("00000000-0000-0000-0000-000000000001")
WS2 = UUID("00000000-0000-0000-0000-000000000002")


class TestDocumentEntity:
    """Verify the Document entity follows clean architecture rules."""

    def test_document_creation(self) -> None:
        doc = Document(workspace_id=WS1)
        assert doc.workspace_id == WS1

    def test_document_has_unique_id(self) -> None:
        doc1 = Document(workspace_id=WS1)
        doc2 = Document(workspace_id=WS2)
        assert isinstance(doc1.document_id, UUID)
        assert doc1.document_id != doc2.document_id

    def test_document_no_external_dependencies(self) -> None:
        """Verify the entity module has only stdlib or domain-internal imports."""
        import ast
        import sys

        import domain.entities.document as doc_module

        source = doc_module.__file__ or ""
        with open(source) as f:
            tree = ast.parse(f.read())

        stdlib = sys.stdlib_module_names
        internal_packages = {"domain"}

        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    top = alias.name.split(".")[0]
                    assert top in stdlib or top in internal_packages, f"Domain entity imports non-stdlib: {alias.name}"
            elif isinstance(node, ast.ImportFrom) and node.module:
                top = node.module.split(".")[0]
                assert top in stdlib or top in internal_packages, f"Domain entity imports non-stdlib: {node.module}"

    def test_document_default_status(self) -> None:
        doc = Document(workspace_id=WS1)
        assert doc.status.value == "FILE_UPLOAD_PENDING"

    def test_document_default_checksum_none(self) -> None:
        doc = Document(workspace_id=WS1)
        assert doc.checksum is None

    def test_document_default_size_none(self) -> None:
        doc = Document(workspace_id=WS1)
        assert doc.size is None
