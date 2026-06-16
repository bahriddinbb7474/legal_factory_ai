"""curated legal rag

Revision ID: 0006_curated_legal_rag
Revises: 0005_verdict_generated_documents
Create Date: 2026-06-16
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0006_curated_legal_rag"
down_revision: str | None = "0005_verdict_generated_documents"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "legal_sources",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("document_type", sa.String(length=64), nullable=False),
        sa.Column("title", sa.String(length=500), nullable=False),
        sa.Column("document_number", sa.String(length=128), nullable=True),
        sa.Column("source_name", sa.String(length=255), nullable=False),
        sa.Column("source_url", sa.String(length=1000), nullable=True),
        sa.Column("adoption_date", sa.String(length=32), nullable=True),
        sa.Column("revision_date", sa.String(length=32), nullable=True),
        sa.Column("last_checked_at", sa.DateTime(), nullable=True),
        sa.Column("next_check_due_at", sa.DateTime(), nullable=True),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("status", sa.String(length=32), nullable=False),
        sa.Column("official_status", sa.String(length=32), nullable=False),
        sa.Column("uploaded_by_user_id", sa.Integer(), nullable=True),
        sa.Column("storage_key", sa.String(length=500), nullable=False),
        sa.ForeignKeyConstraint(["uploaded_by_user_id"], ["users.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_legal_sources_id", "legal_sources", ["id"], unique=False)
    op.create_index("ix_legal_sources_document_type", "legal_sources", ["document_type"], unique=False)
    op.create_index("ix_legal_sources_status", "legal_sources", ["status"], unique=False)
    op.create_index("ix_legal_sources_official_status", "legal_sources", ["official_status"], unique=False)

    op.create_table(
        "legal_chunks",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("legal_source_id", sa.Integer(), nullable=False),
        sa.Column("article_or_point", sa.String(length=255), nullable=True),
        sa.Column("section_title", sa.String(length=500), nullable=True),
        sa.Column("chunk_index", sa.Integer(), nullable=False),
        sa.Column("chunk_text", sa.Text(), nullable=False),
        sa.Column("embedding", sa.JSON(), nullable=True),
        sa.Column("metadata_json", sa.JSON(), nullable=True),
        sa.ForeignKeyConstraint(["legal_source_id"], ["legal_sources.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_legal_chunks_id", "legal_chunks", ["id"], unique=False)
    op.create_index("ix_legal_chunks_legal_source_id", "legal_chunks", ["legal_source_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_legal_chunks_legal_source_id", table_name="legal_chunks")
    op.drop_index("ix_legal_chunks_id", table_name="legal_chunks")
    op.drop_table("legal_chunks")

    op.drop_index("ix_legal_sources_official_status", table_name="legal_sources")
    op.drop_index("ix_legal_sources_status", table_name="legal_sources")
    op.drop_index("ix_legal_sources_document_type", table_name="legal_sources")
    op.drop_index("ix_legal_sources_id", table_name="legal_sources")
    op.drop_table("legal_sources")
