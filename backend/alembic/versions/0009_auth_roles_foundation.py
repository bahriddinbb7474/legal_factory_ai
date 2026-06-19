"""auth and roles foundation

Revision ID: 0009_auth_roles_foundation
Revises: 0008_document_template_foundation
Create Date: 2026-06-19
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op

revision: str = "0009_auth_roles_foundation"
down_revision: str | None = "0008_document_template_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("users") as batch_op:
        batch_op.add_column(sa.Column("role", sa.String(length=64), server_default="viewer", nullable=False))
        batch_op.add_column(sa.Column("password_hash", sa.String(length=500), server_default="", nullable=False))
        batch_op.add_column(sa.Column("last_login_at", sa.DateTime(), nullable=True))
        batch_op.create_index("ix_users_role", ["role"], unique=False)
        batch_op.create_check_constraint("ck_users_role", "role IN ('admin','director','chief_accountant','legal_responsible','sales','supply','hr','accountant','viewer')")
        batch_op.alter_column("role", server_default=None)
        batch_op.alter_column("password_hash", server_default=None)

    op.create_table(
        "auth_sessions",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("token_hash", sa.String(length=64), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("expires_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_auth_sessions_id", "auth_sessions", ["id"], unique=False)
    op.create_index("ix_auth_sessions_token_hash", "auth_sessions", ["token_hash"], unique=True)
    op.create_index("ix_auth_sessions_user_id", "auth_sessions", ["user_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_auth_sessions_user_id", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_token_hash", table_name="auth_sessions")
    op.drop_index("ix_auth_sessions_id", table_name="auth_sessions")
    op.drop_table("auth_sessions")
    with op.batch_alter_table("users") as batch_op:
        batch_op.drop_constraint("ck_users_role", type_="check")
        batch_op.drop_index("ix_users_role")
        batch_op.drop_column("last_login_at")
        batch_op.drop_column("password_hash")
        batch_op.drop_column("role")
