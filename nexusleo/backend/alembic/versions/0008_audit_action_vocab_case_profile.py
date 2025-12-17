"""expand audit action vocabulary for case_profile_set

Revision ID: 0008_case_profile_audit
Revises: 0007_case_profile_id
Create Date: 2025-12-16

"""
from __future__ import annotations

from alembic import op


revision = "0008_case_profile_audit"
down_revision = "0007_case_profile_id"
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
    "shift_note_logged",
    "activity_attached",
    "case_profile_set",
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
            "'shift_started'",
            "'shift_ended'",
            "'activity_logged'",
            "'shift_note_logged'",
            "'activity_attached'",
        ]
    )
    op.create_check_constraint(
        "audit_action_allowed",
        "audit_events",
        f"action IN ({allowed_sql})",
    )
