"""add_impact_provenance_columns

Revision ID: 9f42c8a1d703
Revises: 8e21b6f9c302
Create Date: 2026-11-28 13:52:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "9f42c8a1d703"
down_revision: Union[str, Sequence[str], None] = "8e21b6f9c302"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Add reproducible calculation provenance columns to impact_records."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("impact_records")}

    if "baseline_co2e_kg" not in cols:
        op.add_column("impact_records", sa.Column("baseline_co2e_kg", sa.Numeric(10, 4), nullable=True))
    if "alternative_co2e_kg" not in cols:
        op.add_column("impact_records", sa.Column("alternative_co2e_kg", sa.Numeric(10, 4), nullable=True))
    if "method_version" not in cols:
        op.add_column(
            "impact_records",
            sa.Column("method_version", sa.String(length=40), server_default="airwise_transport_v1", nullable=False),
        )
    if "factor_snapshot" not in cols:
        op.add_column(
            "impact_records",
            sa.Column("factor_snapshot", sa.JSON(), server_default="{}", nullable=False),
        )


def downgrade() -> None:
    """Revert Phase 7 provenance columns."""
    bind = op.get_bind()
    inspector = sa.inspect(bind)
    cols = {c["name"] for c in inspector.get_columns("impact_records")}
    for col in ("factor_snapshot", "method_version", "alternative_co2e_kg", "baseline_co2e_kg"):
        if col in cols:
            op.drop_column("impact_records", col)
