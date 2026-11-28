"""add_planner_fields_to_daily_routines

Revision ID: 8e21b6f9c302
Revises: 7c91a4e2b801
Create Date: 2026-11-28 13:18:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "8e21b6f9c302"
down_revision: Union[str, Sequence[str], None] = "7c91a4e2b801"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add Phase 6 daily planner columns to daily_routines safely."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("daily_routines")}
    indexes = {i["name"] for i in inspector.get_indexes("daily_routines")}

    op.alter_column("daily_routines", "name", type_=sa.String(length=160), existing_type=sa.String(length=100))
    op.alter_column("daily_routines", "routine_type", type_=sa.String(length=30), existing_type=sa.String(length=20))

    if "description" not in cols:
        op.add_column("daily_routines", sa.Column("description", sa.Text(), nullable=True))
    if "routine_date" not in cols:
        op.add_column("daily_routines", sa.Column("routine_date", sa.Date(), nullable=True))
    if "status" not in cols:
        op.add_column(
            "daily_routines",
            sa.Column("status", sa.String(length=20), server_default="planned", nullable=False),
        )
    if "reminder_minutes" not in cols:
        op.add_column("daily_routines", sa.Column("reminder_minutes", sa.Integer(), nullable=True))
    if "source_recommendation_id" not in cols:
        op.add_column(
            "daily_routines",
            sa.Column(
                "source_recommendation_id",
                sa.Uuid(),
                sa.ForeignKey("recommendations.id", ondelete="SET NULL"),
                nullable=True,
            ),
        )
    if "ix_daily_routines_user_date" not in indexes:
        op.create_index("ix_daily_routines_user_date", "daily_routines", ["user_id", "routine_date"], unique=False)


def downgrade() -> None:
    """Revert Phase 6 daily planner columns."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("daily_routines")}
    indexes = {i["name"] for i in inspector.get_indexes("daily_routines")}

    if "ix_daily_routines_user_date" in indexes:
        op.drop_index("ix_daily_routines_user_date", table_name="daily_routines")
    for col_name in ("source_recommendation_id", "reminder_minutes", "status", "routine_date", "description"):
        if col_name in cols:
            op.drop_column("daily_routines", col_name)
