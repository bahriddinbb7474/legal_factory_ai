"""add section to chats

Revision ID: 0010_chat_section
Revises: 0009_auth_roles_foundation
Create Date: 2026-06-23
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0010_chat_section"
down_revision: str | None = "0009_auth_roles_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("chats") as batch_op:
        batch_op.add_column(sa.Column("section", sa.String(length=128), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table("chats") as batch_op:
        batch_op.drop_column("section")
