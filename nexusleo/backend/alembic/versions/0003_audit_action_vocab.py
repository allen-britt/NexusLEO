"""expand audit action vocabulary

Revision ID: 0003_audit_action_vocab
Revises: 0002_shift_activity_logging
Create Date: 2025-12-16

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0003_audit_action_vocab"
down_revision = "0002_shift_activity_logging"
branch_labels = None
depends_on = None


_ALLOWED = (
    "ingest_started",
    "extraction_completed",
    "confidence_assessed",
    "ingest_completed",
    "shift_started",
    "shift_ended",
    "activity_logged",
)


def upgrade() -> None:
    op.drop_constraint("audit_action_allowed", "audit_events", type_="check")
    allowed_sql = ",".join([f"'{a}'" for a in _ALLOWED])
    op.create_check_constraint(
        "audit_action_allowed",
        "audit_events",
        f"action IN ({allowed_sql})",
    )


def downgrade() -> None:
    op.drop_constraint("audit_action_allowed", "audit_events", type_="check")
    allowed_sql = ",".join(
        [
            "'ingest_started'",
            "'extraction_completed'",
            "'confidence_assessed'",
            "'ingest_completed'",
        ]
    )
    op.create_check_constraint(
        "audit_action_allowed",
        "audit_events",
        f"action IN ({allowed_sql})",
    )
