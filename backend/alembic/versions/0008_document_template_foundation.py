"""document template foundation

Revision ID: 0008_document_template_foundation
Revises: 0007_company_profile_foundation
Create Date: 2026-06-18
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0008_document_template_foundation"
down_revision: str | None = "0007_company_profile_foundation"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    with op.batch_alter_table("generated_documents") as batch_op:
        batch_op.add_column(sa.Column("template_key", sa.String(length=128), nullable=True))
        batch_op.create_index("ix_generated_documents_template_key", ["template_key"], unique=False)

    op.create_table(
        "document_templates",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("template_key", sa.String(length=128), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=False),
        sa.Column("description", sa.Text(), nullable=False),
        sa.Column("category", sa.String(length=64), nullable=False),
        sa.Column("language", sa.String(length=32), nullable=False),
        sa.Column("template_type", sa.String(length=64), nullable=False),
        sa.Column("body_template", sa.Text(), nullable=False),
        sa.Column("docx_template_storage_key", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("requires_approval", sa.Boolean(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_document_templates_id", "document_templates", ["id"], unique=False)
    op.create_index("ix_document_templates_template_key", "document_templates", ["template_key"], unique=True)
    op.create_index("ix_document_templates_category", "document_templates", ["category"], unique=False)
    op.create_index("ix_document_templates_is_active", "document_templates", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_document_templates_is_active", table_name="document_templates")
    op.drop_index("ix_document_templates_category", table_name="document_templates")
    op.drop_index("ix_document_templates_template_key", table_name="document_templates")
    op.drop_index("ix_document_templates_id", table_name="document_templates")
    op.drop_table("document_templates")

    with op.batch_alter_table("generated_documents") as batch_op:
        batch_op.drop_index("ix_generated_documents_template_key")
        batch_op.drop_column("template_key")
