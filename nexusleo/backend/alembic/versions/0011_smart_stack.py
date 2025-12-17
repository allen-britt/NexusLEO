"""Internal smart stack v0.1: catalogs and selections."""
from __future__ import annotations

import uuid

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0011_smart_stack"
down_revision = "0010_artifact_added_audit"
branch_labels = None
depends_on = None


def _create_audit_constraint_with(values: tuple[str, ...]) -> None:
    op.drop_constraint("audit_action_allowed", "audit_events", type_="check")
    allowed_sql = ",".join([f"'{a}'" for a in values])
    op.create_check_constraint("audit_action_allowed", "audit_events", f"action IN ({allowed_sql})")


def upgrade() -> None:
    op.create_table(
        "code_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("jurisdiction", sa.String(), nullable=False),
        sa.Column("system", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_code_catalog_jurisdiction", "code_catalog", ["jurisdiction"])
    op.create_index("ix_code_catalog_code", "code_catalog", ["code"])
    op.create_index("ix_code_catalog_active", "code_catalog", ["active"])

    op.create_table(
        "call_type_catalog",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("jurisdiction", sa.String(), nullable=False),
        sa.Column("system", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("tags_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_call_type_catalog_jurisdiction", "call_type_catalog", ["jurisdiction"])
    op.create_index("ix_call_type_catalog_code", "call_type_catalog", ["code"])
    op.create_index("ix_call_type_catalog_active", "call_type_catalog", ["active"])

    op.create_table(
        "case_code_selections",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("catalog_type", sa.String(), nullable=False),
        sa.Column("code_catalog_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("code_catalog.id", ondelete="CASCADE"), nullable=True),
        sa.Column("call_type_catalog_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("call_type_catalog.id", ondelete="CASCADE"), nullable=True),
        sa.Column("selected_by", sa.String(), nullable=False, server_default=sa.text("'system'")),
        sa.Column("selected_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("note", sa.Text(), nullable=True),
        sa.CheckConstraint("catalog_type in ('CODE','CALL_TYPE')", name="catalog_type_allowed"),
        sa.CheckConstraint(
            "(catalog_type = 'CODE' and code_catalog_id is not null and call_type_catalog_id is null)"
            " or (catalog_type = 'CALL_TYPE' and call_type_catalog_id is not null and code_catalog_id is null)",
            name="catalog_reference_match",
        ),
    )
    op.create_index("ix_case_code_selection_case_id", "case_code_selections", ["case_id"])
    op.create_index("ix_case_code_selection_selected_at", "case_code_selections", ["selected_at"])
    op.create_index(
        "uq_case_code_selection_code",
        "case_code_selections",
        ["case_id", "code_catalog_id"],
        unique=True,
        postgresql_where=sa.text("catalog_type = 'CODE'"),
    )
    op.create_index(
        "uq_case_code_selection_call_type",
        "case_code_selections",
        ["case_id", "call_type_catalog_id"],
        unique=True,
        postgresql_where=sa.text("catalog_type = 'CALL_TYPE'"),
    )

    op.add_column(
        "cases",
        sa.Column("state_context_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )
    op.add_column(
        "cases",
        sa.Column("observed_facts_json", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
    )

    _create_audit_constraint_with(
        (
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
            "code_selected",
        )
    )

    code_catalog_table = sa.table(
        "code_catalog",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("jurisdiction", sa.String()),
        sa.column("system", sa.String()),
        sa.column("code", sa.String()),
        sa.column("label", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("tags_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("active", sa.Boolean()),
    )

    call_type_catalog_table = sa.table(
        "call_type_catalog",
        sa.column("id", postgresql.UUID(as_uuid=True)),
        sa.column("jurisdiction", sa.String()),
        sa.column("system", sa.String()),
        sa.column("code", sa.String()),
        sa.column("label", sa.String()),
        sa.column("description", sa.Text()),
        sa.column("tags_json", postgresql.JSONB(astext_type=sa.Text())),
        sa.column("active", sa.Boolean()),
    )

    op.bulk_insert(
        code_catalog_table,
        [
            {
                "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaa0001"),
                "jurisdiction": "MD",
                "system": "LOCAL",
                "code": "SPD",
                "label": "Speeding",
                "description": "Observed speeding over posted limit.",
                "tags_json": {"tags": ["speeding", "traffic"]},
                "active": True,
            },
            {
                "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaa0002"),
                "jurisdiction": "MD",
                "system": "LOCAL",
                "code": "WEAPON",
                "label": "Weapon involved",
                "description": "Weapon present or displayed.",
                "tags_json": {"tags": ["weapon"]},
                "active": True,
            },
        ],
    )

    op.bulk_insert(
        call_type_catalog_table,
        [
            {
                "id": uuid.UUID("aaaaaaaa-aaaa-aaaa-aaaa-aaaaaaaa1001"),
                "jurisdiction": "MD",
                "system": "LOCAL",
                "code": "SCHOOL_ZONE",
                "label": "School zone call",
                "description": "Incident located in a school zone.",
                "tags_json": {"tags": ["school_zone"]},
                "active": True,
            },
        ],
    )


def downgrade() -> None:
    op.drop_column("cases", "observed_facts_json")
    op.drop_column("cases", "state_context_json")

    op.drop_index("uq_case_code_selection_call_type", table_name="case_code_selections")
    op.drop_index("uq_case_code_selection_code", table_name="case_code_selections")
    op.drop_index("ix_case_code_selection_selected_at", table_name="case_code_selections")
    op.drop_index("ix_case_code_selection_case_id", table_name="case_code_selections")
    op.drop_table("case_code_selections")

    op.drop_index("ix_call_type_catalog_active", table_name="call_type_catalog")
    op.drop_index("ix_call_type_catalog_code", table_name="call_type_catalog")
    op.drop_index("ix_call_type_catalog_jurisdiction", table_name="call_type_catalog")
    op.drop_table("call_type_catalog")

    op.drop_index("ix_code_catalog_active", table_name="code_catalog")
    op.drop_index("ix_code_catalog_code", table_name="code_catalog")
    op.drop_index("ix_code_catalog_jurisdiction", table_name="code_catalog")
    op.drop_table("code_catalog")

    _create_audit_constraint_with(
        (
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
    )
