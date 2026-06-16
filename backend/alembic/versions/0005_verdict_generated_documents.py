"""verdict generated documents

Revision ID: 0005_verdict_generated_documents
Revises: 0004_structured_legal_safeguards
Create Date: 2026-06-16
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0005_verdict_generated_documents"
down_revision: str | None = "0004_structured_legal_safeguards"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("chats") as batch_op:
        batch_op.add_column(sa.Column("active_verdict_message_id", sa.Integer(), nullable=True))

    with op.batch_alter_table("messages") as batch_op:
        batch_op.add_column(sa.Column("is_verdict", sa.Boolean(), server_default=sa.false(), nullable=False))

    op.create_table(
        "generated_documents",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("verdict_message_id", sa.Integer(), nullable=False),
        sa.Column("created_by_agent_id", sa.Integer(), nullable=True),
        sa.Column("title", sa.String(length=255), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("content", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("storage_key", sa.String(length=500), nullable=True),
        sa.Column("docx_storage_key", sa.String(length=500), nullable=True),
        sa.Column("pdf_storage_key", sa.String(length=500), nullable=True),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"]),
        sa.ForeignKeyConstraint(["verdict_message_id"], ["messages.id"]),
        sa.ForeignKeyConstraint(["created_by_agent_id"], ["agents.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_generated_documents_id", "generated_documents", ["id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_generated_documents_id", table_name="generated_documents")
    op.drop_table("generated_documents")

    with op.batch_alter_table("messages") as batch_op:
        batch_op.drop_column("is_verdict")

    with op.batch_alter_table("chats") as batch_op:
        batch_op.drop_column("active_verdict_message_id")
