"""Create documents table

Revision ID: 001
Revises:
Create Date: 2026-05-14
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "documents",
        sa.Column("document_id", UUID(as_uuid=True), primary_key=True),
        sa.Column("workspace_id", UUID(as_uuid=True), nullable=False),
        sa.Column("checksum", sa.String(64), nullable=True),
        sa.Column("size", sa.BigInteger(), nullable=True),
        sa.Column("status", sa.String(50), nullable=False, server_default="FILE_UPLOAD_PENDING"),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("s3_storage_path", sa.String(1024), nullable=True),
        sa.Column("mime_type", sa.String(127), nullable=True),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.func.now(),
            nullable=False,
        ),
    )
    op.create_unique_constraint(
        "uq_documents_workspace_checksum",
        "documents",
        ["workspace_id", "checksum"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_documents_workspace_checksum", "documents")
    op.drop_table("documents")
