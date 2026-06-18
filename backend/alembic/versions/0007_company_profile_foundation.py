"""company profile foundation

Revision ID: 0007_company_profile_foundation
Revises: 0006_curated_legal_rag
Create Date: 2026-06-18
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0007_company_profile_foundation"
down_revision: str | None = "0006_curated_legal_rag"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "company_profiles",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.Column("full_name", sa.String(length=500), nullable=False),
        sa.Column("short_name", sa.String(length=255), nullable=False),
        sa.Column("legal_address", sa.Text(), nullable=True),
        sa.Column("actual_address", sa.Text(), nullable=True),
        sa.Column("tax_id", sa.String(length=128), nullable=True),
        sa.Column("oked", sa.String(length=128), nullable=True),
        sa.Column("bank_name", sa.String(length=255), nullable=True),
        sa.Column("bank_mfo", sa.String(length=64), nullable=True),
        sa.Column("bank_account", sa.String(length=128), nullable=True),
        sa.Column("director_name", sa.String(length=255), nullable=True),
        sa.Column("chief_accountant_name", sa.String(length=255), nullable=True),
        sa.Column("legal_responsible_name", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=128), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.Column("website", sa.String(length=500), nullable=True),
        sa.Column("logo_storage_key", sa.String(length=500), nullable=True),
        sa.Column("letterhead_storage_key", sa.String(length=500), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("notes", sa.Text(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_company_profiles_id", "company_profiles", ["id"], unique=False)
    op.create_index("ix_company_profiles_is_active", "company_profiles", ["is_active"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_company_profiles_is_active", table_name="company_profiles")
    op.drop_index("ix_company_profiles_id", table_name="company_profiles")
    op.drop_table("company_profiles")
