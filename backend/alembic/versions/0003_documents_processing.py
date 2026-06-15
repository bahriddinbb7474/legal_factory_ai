"""document upload and secure processing

Revision ID: 0003_documents_processing
Revises: 0002_openrouter_lawyers
Create Date: 2026-06-15
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0003_documents_processing"
down_revision: str | None = "0002_openrouter_lawyers"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("documents") as batch_op:
        batch_op.add_column(sa.Column("original_filename", sa.String(length=255), server_default="", nullable=False))
        batch_op.add_column(sa.Column("storage_key", sa.String(length=500), server_default="", nullable=False))
        batch_op.add_column(sa.Column("mime_type", sa.String(length=128), server_default="", nullable=False))
        batch_op.add_column(sa.Column("file_size", sa.Integer(), server_default="0", nullable=False))
        batch_op.add_column(sa.Column("file_hash", sa.String(length=64), server_default="", nullable=False))
        batch_op.add_column(sa.Column("category", sa.String(length=64), server_default="other", nullable=False))
        batch_op.add_column(sa.Column("suggested_category", sa.String(length=64), server_default="other", nullable=False))
        batch_op.add_column(sa.Column("counterparty", sa.String(length=255), nullable=True))
        batch_op.add_column(sa.Column("document_number", sa.String(length=128), nullable=True))
        batch_op.add_column(sa.Column("document_date", sa.String(length=32), nullable=True))
        batch_op.add_column(sa.Column("sensitivity", sa.String(length=32), server_default="normal", nullable=False))
        batch_op.add_column(sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("extraction_status", sa.String(length=32), server_default="pending", nullable=False))
        batch_op.add_column(sa.Column("extracted_text_storage_key", sa.String(length=500), nullable=True))
        batch_op.add_column(sa.Column("ocr_status", sa.String(length=32), server_default="not_required", nullable=False))
        batch_op.create_foreign_key("fk_documents_uploaded_by_user_id_users", "users", ["uploaded_by_user_id"], ["id"])
        batch_op.create_index("ix_documents_file_hash", ["file_hash"])
        batch_op.create_index("ix_documents_category", ["category"])
        batch_op.create_index("ix_documents_sensitivity", ["sensitivity"])

    op.execute("UPDATE documents SET original_filename = filename WHERE original_filename = ''")
    op.execute("UPDATE documents SET storage_key = storage_path WHERE storage_key = ''")
    op.execute("UPDATE documents SET mime_type = file_type WHERE mime_type = ''")

    op.create_table(
        "chat_documents",
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("added_by_user_id", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["added_by_user_id"], ["users.id"]),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"]),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.PrimaryKeyConstraint("chat_id", "document_id"),
    )
    op.create_index("ix_chat_documents_chat_id", "chat_documents", ["chat_id"], unique=False)
    op.create_index("ix_chat_documents_document_id", "chat_documents", ["document_id"], unique=False)

    op.create_table(
        "message_documents",
        sa.Column("message_id", sa.Integer(), nullable=False),
        sa.Column("document_id", sa.Integer(), nullable=False),
        sa.Column("usage_type", sa.String(length=32), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["document_id"], ["documents.id"]),
        sa.ForeignKeyConstraint(["message_id"], ["messages.id"]),
        sa.PrimaryKeyConstraint("message_id", "document_id", "usage_type"),
    )
    op.create_index("ix_message_documents_message_id", "message_documents", ["message_id"], unique=False)
    op.create_index("ix_message_documents_document_id", "message_documents", ["document_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_message_documents_document_id", table_name="message_documents")
    op.drop_index("ix_message_documents_message_id", table_name="message_documents")
    op.drop_table("message_documents")
    op.drop_index("ix_chat_documents_document_id", table_name="chat_documents")
    op.drop_index("ix_chat_documents_chat_id", table_name="chat_documents")
    op.drop_table("chat_documents")

    with op.batch_alter_table("documents") as batch_op:
        batch_op.drop_index("ix_documents_sensitivity")
        batch_op.drop_index("ix_documents_category")
        batch_op.drop_index("ix_documents_file_hash")
        batch_op.drop_constraint("fk_documents_uploaded_by_user_id_users", type_="foreignkey")
        batch_op.drop_column("ocr_status")
        batch_op.drop_column("extracted_text_storage_key")
        batch_op.drop_column("extraction_status")
        batch_op.drop_column("uploaded_by_user_id")
        batch_op.drop_column("sensitivity")
        batch_op.drop_column("document_date")
        batch_op.drop_column("document_number")
        batch_op.drop_column("counterparty")
        batch_op.drop_column("suggested_category")
        batch_op.drop_column("category")
        batch_op.drop_column("file_hash")
        batch_op.drop_column("file_size")
        batch_op.drop_column("mime_type")
        batch_op.drop_column("storage_key")
        batch_op.drop_column("original_filename")
