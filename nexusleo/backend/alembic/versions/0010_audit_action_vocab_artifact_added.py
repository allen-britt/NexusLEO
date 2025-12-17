from __future__ import annotations

from alembic import op


revision = "0010_artifact_added_audit"
down_revision = "0009_evidence_artifacts"
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
    "artifact_added",
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
            "'case_profile_set'",
        ]
    )
    op.create_check_constraint(
        "audit_action_allowed",
        "audit_events",
        f"action IN ({allowed_sql})",
    )
