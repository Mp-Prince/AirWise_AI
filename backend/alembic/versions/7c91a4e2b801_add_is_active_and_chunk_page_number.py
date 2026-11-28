"""add_is_active_and_chunk_page_number

Revision ID: 7c91a4e2b801
Revises: 2b32ab00aaf5
Create Date: 2026-11-28 11:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "7c91a4e2b801"
down_revision: Union[str, Sequence[str], None] = "2b32ab00aaf5"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add is_active to knowledge_documents and page_number to document_chunks."""
    op.add_column(
        "knowledge_documents",
        sa.Column("is_active", sa.Boolean(), server_default=sa.true(), nullable=False),
    )
    op.add_column(
        "document_chunks",
        sa.Column("page_number", sa.Integer(), nullable=True),
    )


def downgrade() -> None:
    """Revert Phase 4 metadata column additions."""
    op.drop_column("document_chunks", "page_number")
    op.drop_column("knowledge_documents", "is_active")
