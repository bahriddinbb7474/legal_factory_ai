"""add backend document generation gate

Revision ID: 0012_verdict_response_skeleton
Revises: 0011_app_settings
Create Date: 2026-06-29
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0012_verdict_response_skeleton"
down_revision: str | None = "0011_app_settings"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(
            sa.Column("document_generation_allowed", sa.Boolean(), server_default=sa.false(), nullable=False)
        )


def downgrade() -> None:
    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_column("document_generation_allowed")
