"""shift + activity logging

Revision ID: 0002_shift_activity_logging
Revises: 0001_core_schema
Create Date: 2025-12-16

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0002_shift_activity_logging"
down_revision = "0001_core_schema"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("display_name", sa.String(), nullable=False),
        sa.Column("badge_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "shift_sessions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("started_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("ended_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("device_id", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_shift_session_user_id", "shift_sessions", ["user_id"], unique=False)
    op.create_index("ix_shift_session_started_at", "shift_sessions", ["started_at"], unique=False)

    op.create_table(
        "activity_log_entries",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "shift_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("shift_sessions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "case_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("cases.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("occurred_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("entry_type", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column(
            "metadata_json",
            postgresql.JSONB(astext_type=sa.Text()),
            nullable=False,
            server_default=sa.text("'{}'::jsonb"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_activity_log_entry_shift_id", "activity_log_entries", ["shift_id"], unique=False)
    op.create_index("ix_activity_log_entry_case_id", "activity_log_entries", ["case_id"], unique=False)
    op.create_index("ix_activity_log_entry_occurred_at", "activity_log_entries", ["occurred_at"], unique=False)
    op.create_index("ix_activity_log_entry_created_at", "activity_log_entries", ["created_at"], unique=False)

    op.alter_column("audit_events", "case_id", existing_type=postgresql.UUID(as_uuid=True), nullable=True)


def downgrade() -> None:
    op.alter_column("audit_events", "case_id", existing_type=postgresql.UUID(as_uuid=True), nullable=False)

    op.drop_index("ix_activity_log_entry_created_at", table_name="activity_log_entries")
    op.drop_index("ix_activity_log_entry_occurred_at", table_name="activity_log_entries")
    op.drop_index("ix_activity_log_entry_case_id", table_name="activity_log_entries")
    op.drop_index("ix_activity_log_entry_shift_id", table_name="activity_log_entries")
    op.drop_table("activity_log_entries")

    op.drop_index("ix_shift_session_started_at", table_name="shift_sessions")
    op.drop_index("ix_shift_session_user_id", table_name="shift_sessions")
    op.drop_table("shift_sessions")

    op.drop_table("users")
