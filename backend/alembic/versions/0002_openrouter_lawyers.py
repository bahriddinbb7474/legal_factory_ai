"""openrouter lawyers and model settings

Revision ID: 0002_openrouter_lawyers
Revises: 0001_initial
Create Date: 2026-06-15
"""
from collections.abc import Sequence

import sqlalchemy as sa
from alembic import op


revision: str = "0002_openrouter_lawyers"
down_revision: str | None = "0001_initial"
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    op.create_table(
        "provider_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("provider_code", sa.String(length=64), nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column("is_allowlisted", sa.Boolean(), nullable=False),
        sa.Column("supports_zdr", sa.Boolean(), nullable=False),
        sa.Column("is_trusted_for_sensitive", sa.Boolean(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_provider_configs_id"), "provider_configs", ["id"], unique=False)
    op.create_index(op.f("ix_provider_configs_provider_code"), "provider_configs", ["provider_code"], unique=True)

    op.create_table(
        "model_configs",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("agent_code", sa.String(length=32), nullable=False),
        sa.Column("provider_code", sa.String(length=64), nullable=False),
        sa.Column("model_name", sa.String(length=255), nullable=False),
        sa.Column("input_price_per_1m", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("output_price_per_1m", sa.Numeric(precision=12, scale=6), nullable=False),
        sa.Column("max_context_tokens", sa.Integer(), nullable=False),
        sa.Column("supports_structured_output", sa.Boolean(), nullable=False),
        sa.Column("supports_vision", sa.Boolean(), nullable=False),
        sa.Column("is_enabled", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_model_configs_agent_code"), "model_configs", ["agent_code"], unique=False)
    op.create_index(op.f("ix_model_configs_id"), "model_configs", ["id"], unique=False)
    op.create_index(op.f("ix_model_configs_provider_code"), "model_configs", ["provider_code"], unique=False)

    op.add_column("agents", sa.Column("display_name", sa.String(length=255), server_default="", nullable=False))
    op.add_column("agents", sa.Column("provider_code", sa.String(length=64), server_default="", nullable=False))
    op.add_column("agents", sa.Column("system_prompt", sa.Text(), server_default="", nullable=False))
    op.add_column("agents", sa.Column("role_type", sa.String(length=64), server_default="", nullable=False))
    op.add_column(
        "agents",
        sa.Column("input_price_per_1m", sa.Numeric(precision=12, scale=6), server_default="0", nullable=False),
    )
    op.add_column(
        "agents",
        sa.Column("output_price_per_1m", sa.Numeric(precision=12, scale=6), server_default="0", nullable=False),
    )
    op.add_column("agents", sa.Column("supports_zdr", sa.Boolean(), server_default=sa.false(), nullable=False))

    # Safe while no production data exists. Existing assistant messages are treated as lawyer_1.
    op.add_column("messages", sa.Column("author_type", sa.String(length=32), nullable=True))
    op.execute("UPDATE messages SET author_type = CASE WHEN role = 'assistant' THEN 'agent1' ELSE role END")
    op.alter_column("messages", "author_type", nullable=False)
    op.add_column("messages", sa.Column("model_id", sa.String(length=255), nullable=True))
    op.add_column("messages", sa.Column("provider_code", sa.String(length=64), nullable=True))
    op.add_column("messages", sa.Column("input_tokens", sa.Integer(), server_default="0", nullable=False))
    op.add_column("messages", sa.Column("output_tokens", sa.Integer(), server_default="0", nullable=False))
    op.add_column(
        "messages",
        sa.Column("cost_usd", sa.Numeric(precision=12, scale=6), server_default="0", nullable=False),
    )

    op.add_column("cost_records", sa.Column("provider_code", sa.String(length=64), nullable=True))
    op.add_column("cost_records", sa.Column("model_id", sa.String(length=255), nullable=True))


def downgrade() -> None:
    op.drop_column("cost_records", "model_id")
    op.drop_column("cost_records", "provider_code")
    op.drop_column("messages", "cost_usd")
    op.drop_column("messages", "output_tokens")
    op.drop_column("messages", "input_tokens")
    op.drop_column("messages", "provider_code")
    op.drop_column("messages", "model_id")
    op.drop_column("messages", "author_type")
    op.drop_column("agents", "supports_zdr")
    op.drop_column("agents", "output_price_per_1m")
    op.drop_column("agents", "input_price_per_1m")
    op.drop_column("agents", "role_type")
    op.drop_column("agents", "system_prompt")
    op.drop_column("agents", "provider_code")
    op.drop_column("agents", "display_name")
    op.drop_index(op.f("ix_model_configs_provider_code"), table_name="model_configs")
    op.drop_index(op.f("ix_model_configs_id"), table_name="model_configs")
    op.drop_index(op.f("ix_model_configs_agent_code"), table_name="model_configs")
    op.drop_table("model_configs")
    op.drop_index(op.f("ix_provider_configs_provider_code"), table_name="provider_configs")
    op.drop_index(op.f("ix_provider_configs_id"), table_name="provider_configs")
    op.drop_table("provider_configs")
