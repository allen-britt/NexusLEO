"""activity log note linkage

Revision ID: 0004_activity_note_link
Revises: 0003_audit_action_vocab
Create Date: 2025-12-16

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0004_activity_note_link"
down_revision = "0003_audit_action_vocab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column(
        "activity_log_entries",
        sa.Column(
            "source_document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_documents.id", ondelete="SET NULL"),
            nullable=True,
        ),
    )
    op.create_index("ix_activity_log_entry_source_document_id", "activity_log_entries", ["source_document_id"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_activity_log_entry_source_document_id", table_name="activity_log_entries")
    op.drop_column("activity_log_entries", "source_document_id")
