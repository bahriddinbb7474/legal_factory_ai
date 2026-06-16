"""structured legal safeguards

Revision ID: 0004_structured_legal_safeguards
Revises: 0003_documents_processing
Create Date: 2026-06-15
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0004_structured_legal_safeguards"
down_revision: str | None = "0003_documents_processing"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("chats") as batch_op:
        batch_op.add_column(sa.Column("approval_status", sa.String(length=32), server_default="draft", nullable=False))

    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(sa.Column("structured_payload", sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column("raw_response", sa.Text(), nullable=True))
        batch_op.add_column(sa.Column("risk", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("confidence", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("approval_required", sa.String(length=64), nullable=True))
        batch_op.add_column(sa.Column("source_check_status", sa.String(length=32), server_default="not_checked", nullable=False))
        batch_op.add_column(sa.Column("red_flag_codes", sa.JSON(), server_default="[]", nullable=False))

    with op.batch_alter_table("approvals") as batch_op:
        batch_op.add_column(sa.Column("entity_type", sa.String(length=64), server_default="chat", nullable=False))
        batch_op.add_column(sa.Column("entity_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("action", sa.String(length=64), server_default="request", nullable=False))
        batch_op.add_column(sa.Column("performed_by_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("performed_at", sa.DateTime(), nullable=True))
        batch_op.add_column(sa.Column("previous_status", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("new_status", sa.String(length=32), nullable=True))
        batch_op.create_foreign_key("fk_approvals_performed_by_user_id_users", "users", ["performed_by_user_id"], ["id"])

    op.execute("UPDATE approvals SET entity_id = chat_id WHERE entity_id IS NULL")
    op.execute("UPDATE approvals SET performed_by_user_id = approved_by_user_id WHERE performed_by_user_id IS NULL AND approved_by_user_id IS NOT NULL")
    op.execute("UPDATE approvals SET performed_by_user_id = requested_by_user_id WHERE performed_by_user_id IS NULL")
    op.execute("UPDATE approvals SET performed_at = created_at WHERE performed_at IS NULL")
    with op.batch_alter_table("approvals") as batch_op:
        batch_op.alter_column("performed_at", nullable=False)

    op.create_table(
        "red_flag_rules",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("code", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("keywords", sa.JSON(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("amount_threshold", sa.Numeric(14, 2), nullable=True),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("required_approver", sa.String(length=64), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_red_flag_rules_id", "red_flag_rules", ["id"], unique=False)
    op.create_index("ix_red_flag_rules_code", "red_flag_rules", ["code"], unique=True)


def downgrade() -> None:
    op.drop_index("ix_red_flag_rules_code", table_name="red_flag_rules")
    op.drop_index("ix_red_flag_rules_id", table_name="red_flag_rules")
    op.drop_table("red_flag_rules")

    with op.batch_alter_table("approvals") as batch_op:
        batch_op.drop_constraint("fk_approvals_performed_by_user_id_users", type_="foreignkey")
        batch_op.drop_column("new_status")
        batch_op.drop_column("previous_status")
        batch_op.drop_column("performed_at")
        batch_op.drop_column("performed_by_user_id")
        batch_op.drop_column("action")
        batch_op.drop_column("entity_id")
        batch_op.drop_column("entity_type")

    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_column("red_flag_codes")
        batch_op.drop_column("source_check_status")
        batch_op.drop_column("approval_required")
        batch_op.drop_column("confidence")
        batch_op.drop_column("risk")
        batch_op.drop_column("raw_response")
        batch_op.drop_column("structured_payload")

    with op.batch_alter_table("chats") as batch_op:
        batch_op.drop_column("approval_status")
