"""Document entity - placeholder for clean architecture verification."""

from dataclasses import dataclass, field
from uuid import UUID, uuid4


@dataclass
class Document:
    """A domain entity representing an ingested document.

    This is a placeholder entity that verifies the domain layer has
    zero external dependencies (no FastAPI, no SQLAlchemy, etc.).
    """

    title: str
    source_path: str
    id: UUID = field(default_factory=uuid4)

    def __post_init__(self) -> None:
        if not self.title:
            msg = "title must not be empty"
            raise ValueError(msg)
        if not self.source_path:
            msg = "source_path must not be empty"
            raise ValueError(msg)
