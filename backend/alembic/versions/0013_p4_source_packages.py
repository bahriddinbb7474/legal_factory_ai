"""add persistent P4 source packages

Revision ID: 0013_p4_source_packages
Revises: 0012_verdict_response_skeleton
Create Date: 2026-07-02
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0013_p4_source_packages"
down_revision: str | None = "0012_verdict_response_skeleton"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "legal_source_packages",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("protocol_version", sa.String(length=64), nullable=False),
        sa.Column("chat_id", sa.Integer(), nullable=False),
        sa.Column("trigger_message_id", sa.Integer(), nullable=True),
        sa.Column("section_code", sa.String(length=128), nullable=False),
        sa.Column("group_code", sa.String(length=64), nullable=False),
        sa.Column("lawyer_code", sa.String(length=32), nullable=False),
        sa.Column("rag_request_json", sa.JSON(), nullable=False),
        sa.Column("retrieval_query", sa.Text(), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("error_code", sa.String(length=64), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("hash_ready_snapshot_json", sa.JSON(), nullable=False),
        sa.CheckConstraint(
            "status IN ('ready','empty','insufficient','planner_failed','retrieval_failed','blocked_by_policy')",
            name="ck_legal_source_packages_status",
        ),
        sa.ForeignKeyConstraint(["chat_id"], ["chats.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["trigger_message_id"], ["messages.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_legal_source_packages_id", "legal_source_packages", ["id"], unique=False)
    op.create_index("ix_legal_source_packages_chat_id", "legal_source_packages", ["chat_id"], unique=False)
    op.create_index(
        "ix_legal_source_packages_trigger_message_id",
        "legal_source_packages",
        ["trigger_message_id"],
        unique=False,
    )
    op.create_index("ix_legal_source_packages_status", "legal_source_packages", ["status"], unique=False)

    op.create_table(
        "legal_source_package_items",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("package_id", sa.Integer(), nullable=False),
        sa.Column("legal_source_id", sa.Integer(), nullable=True),
        sa.Column("legal_chunk_id", sa.Integer(), nullable=True),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("score", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("source_title_snapshot", sa.String(length=500), nullable=False),
        sa.Column("document_number_snapshot", sa.String(length=128), nullable=True),
        sa.Column("revision_date_snapshot", sa.String(length=32), nullable=True),
        sa.Column("source_url_snapshot", sa.String(length=1000), nullable=True),
        sa.Column("chunk_label_snapshot", sa.String(length=500), nullable=False),
        sa.Column("chunk_text_snapshot", sa.Text(), nullable=False),
        sa.Column("chunk_content_hash", sa.String(length=64), nullable=False),
        sa.ForeignKeyConstraint(["package_id"], ["legal_source_packages.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["legal_source_id"], ["legal_sources.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["legal_chunk_id"], ["legal_chunks.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("package_id", "rank", name="uq_legal_source_package_items_package_rank"),
        sa.UniqueConstraint(
            "package_id",
            "legal_chunk_id",
            name="uq_legal_source_package_items_package_chunk",
        ),
    )
    op.create_index("ix_legal_source_package_items_id", "legal_source_package_items", ["id"], unique=False)
    op.create_index(
        "ix_legal_source_package_items_package_id",
        "legal_source_package_items",
        ["package_id"],
        unique=False,
    )
    op.create_index(
        "ix_legal_source_package_items_legal_source_id",
        "legal_source_package_items",
        ["legal_source_id"],
        unique=False,
    )
    op.create_index(
        "ix_legal_source_package_items_legal_chunk_id",
        "legal_source_package_items",
        ["legal_chunk_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_legal_source_package_items_legal_chunk_id", table_name="legal_source_package_items")
    op.drop_index("ix_legal_source_package_items_legal_source_id", table_name="legal_source_package_items")
    op.drop_index("ix_legal_source_package_items_package_id", table_name="legal_source_package_items")
    op.drop_index("ix_legal_source_package_items_id", table_name="legal_source_package_items")
    op.drop_table("legal_source_package_items")

    op.drop_index("ix_legal_source_packages_status", table_name="legal_source_packages")
    op.drop_index("ix_legal_source_packages_trigger_message_id", table_name="legal_source_packages")
    op.drop_index("ix_legal_source_packages_chat_id", table_name="legal_source_packages")
    op.drop_index("ix_legal_source_packages_id", table_name="legal_source_packages")
    op.drop_table("legal_source_packages")
