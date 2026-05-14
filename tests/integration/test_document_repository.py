"""Integration tests for the DocumentRepository."""

import uuid
from uuid import UUID

import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from configuration.dependencies import create_engine
from domain.entities.document import Document
from domain.value_objects.document_status import DocumentStatus
from infrastructure.persistence.models import Base
from infrastructure.persistence.repositories import DocumentRepository


WS1 = UUID("00000000-0000-0000-0000-000000000001")
WS2 = UUID("00000000-0000-0000-0000-000000000002")


@pytest.mark.integration
class TestDocumentRepository:
    """Tests DocumentRepository with a real PostgreSQL database."""

    @pytest_asyncio.fixture(autouse=True)
    async def setup_db(self) -> None:
        engine = create_engine(...)
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
        self._engine = engine
        yield
        await engine.dispose()

    @pytest_asyncio.fixture
    async def session(self) -> AsyncSession:
        factory = async_sessionmaker(self._engine, class_=AsyncSession, expire_on_commit=False)
        async with factory() as s:
            yield s

    @pytest_asyncio.fixture
    async def repo(self, session: AsyncSession) -> DocumentRepository:
        return DocumentRepository(session)

    @pytest.mark.asyncio
    async def test_save_and_find_by_id(self, repo: DocumentRepository, session: AsyncSession) -> None:
        doc = Document(
            document_id=uuid.uuid4(),
            workspace_id=WS1,
            checksum="abc123",
            size=1024,
            status=DocumentStatus.FILE_UPLOAD_COMPLETED,
        )
        saved = await repo.save(doc)
        await session.commit()

        found = await repo.find_by_id(saved.document_id)
        assert found is not None
        assert found.checksum == "abc123"

    @pytest.mark.asyncio
    async def test_find_by_checksum_and_workspace(self, repo: DocumentRepository, session: AsyncSession) -> None:
        doc = Document(
            document_id=uuid.uuid4(),
            workspace_id=WS1,
            checksum="dup123",
            size=512,
            status=DocumentStatus.FILE_UPLOAD_COMPLETED,
        )
        await repo.save(doc)
        await session.commit()

        found = await repo.find_by_checksum_and_workspace("dup123", WS1)
        assert found is not None
        assert found.document_id == doc.document_id

        not_found = await repo.find_by_checksum_and_workspace("dup123", WS2)
        assert not_found is None

    @pytest.mark.asyncio
    async def test_update_status(self, repo: DocumentRepository, session: AsyncSession) -> None:
        doc = Document(
            document_id=uuid.uuid4(),
            workspace_id=WS1,
        )
        await repo.save(doc)
        await session.commit()

        await repo.update_status(doc.document_id, DocumentStatus.FILE_UPLOAD_FAILED, error_message="corrupted")
        await session.commit()

        found = await repo.find_by_id(doc.document_id)
        assert found is not None
        assert found.status == DocumentStatus.FILE_UPLOAD_FAILED
        assert found.error_message == "corrupted"
