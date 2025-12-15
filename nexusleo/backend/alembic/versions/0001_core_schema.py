"""core schema

Revision ID: 0001_core_schema
Revises: 
Create Date: 2025-12-15

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0001_core_schema"
down_revision = None
branch_labels = None
depends_on = None


_CONFIDENCE_ENUM = "confidence_level"
_RESOLUTION_ENUM = "resolution_hypothesis_status"


def _create_enum_if_not_exists(enum_name: str, values: list[str]) -> None:
    # DO block is used because Postgres has no CREATE TYPE IF NOT EXISTS.
    # Build the enum value list inside SQL via quote_literal to avoid quoting bugs.
    enum_lit = enum_name.replace("'", "''")
    array_items = ",".join(["'" + v.replace("'", "''") + "'" for v in values])
    op.execute(
        sa.text(
            f"""
DO $$
DECLARE
    enum_name text := '{enum_lit}';
    vals text;
BEGIN
    SELECT string_agg(quote_literal(v), ', ') INTO vals
    FROM unnest(ARRAY[{array_items}]) AS v;

    IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = enum_name) THEN
        EXECUTE format('CREATE TYPE %I AS ENUM (%s)', enum_name, vals);
    END IF;
END $$;
"""
        )
    )


def upgrade() -> None:
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto")

    _create_enum_if_not_exists(_CONFIDENCE_ENUM, ["HIGH", "MODERATE", "LOW"])
    _create_enum_if_not_exists(_RESOLUTION_ENUM, ["UNREVIEWED", "ACCEPTED", "REJECTED"])

    op.create_table(
        "cases",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )

    op.create_table(
        "source_documents",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("type", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("raw_text", sa.Text(), nullable=False),
        sa.UniqueConstraint("case_id", "sha256", name="uq_source_document_case_sha"),
    )
    op.create_index("ix_source_document_case_id", "source_documents", ["case_id"], unique=False)
    op.create_index("ix_source_document_sha256", "source_documents", ["sha256"], unique=False)

    op.create_table(
        "mentions",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column(
            "document_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("source_documents.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("start", sa.Integer(), nullable=False),
        sa.Column("end", sa.Integer(), nullable=False),
        sa.Column("speaker", sa.String(), nullable=True),
        sa.Column("timestamp", sa.String(), nullable=True),
        sa.Column("language", sa.String(), nullable=True),
        sa.Column("entity_type_guess", sa.String(), nullable=True),
    )

    op.create_table(
        "entities",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("entity_type", sa.String(), nullable=False),
        sa.Column("canonical_name", sa.String(), nullable=False),
        sa.Column("attributes_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_entity_case_id", "entities", ["case_id"], unique=False)

    op.create_table(
        "claims",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("claim_type", sa.String(), nullable=False),
        sa.Column("subject_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("object_entity_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("entities.id", ondelete="SET NULL"), nullable=True),
        sa.Column("predicate", sa.String(), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_claim_case_id", "claims", ["case_id"], unique=False)

    op.create_table(
        "evidence_links",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False),
        sa.Column("mention_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mentions.id", ondelete="CASCADE"), nullable=False),
        sa.Column("weight", sa.Float(), nullable=False),
        sa.Column("notes", sa.String(), nullable=True),
    )

    op.create_table(
        "confidence_assessments",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("claim_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("claims.id", ondelete="CASCADE"), nullable=False, unique=True),
        sa.Column(
            "level",
            postgresql.ENUM(
                "HIGH",
                "MODERATE",
                "LOW",
                name=_CONFIDENCE_ENUM,
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("rubric_version", sa.String(), nullable=False),
        sa.Column("factors_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("rationale_text", sa.Text(), nullable=False),
    )

    op.create_table(
        "audit_events",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("actor", sa.String(), nullable=False, server_default=sa.text("'system'")),
        sa.Column("action", sa.String(), nullable=False),
        sa.Column("tool", sa.String(), nullable=False),
        sa.Column("tool_version", sa.String(), nullable=False),
        sa.Column("input_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("output_refs_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.CheckConstraint(
            "action IN ('ingest_started','extraction_completed','confidence_assessed','ingest_completed')",
            name="audit_action_allowed",
        ),
    )
    op.create_index("ix_audit_event_case_id", "audit_events", ["case_id"], unique=False)
    op.create_index("ix_audit_event_created_at", "audit_events", ["created_at"], unique=False)

    op.create_table(
        "resolution_hypotheses",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("mention_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("mentions.id", ondelete="CASCADE"), nullable=False),
        sa.Column(
            "candidate_entity_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("entities.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("score", sa.Float(), nullable=False),
        sa.Column("features_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column(
            "status",
            postgresql.ENUM(
                "UNREVIEWED",
                "ACCEPTED",
                "REJECTED",
                name=_RESOLUTION_ENUM,
                create_type=False,
            ),
            nullable=False,
            server_default=sa.text("'UNREVIEWED'"),
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_resolution_hypothesis_mention_id", "resolution_hypotheses", ["mention_id"], unique=False)
    op.create_index(
        "ix_resolution_hypothesis_candidate_entity_id",
        "resolution_hypotheses",
        ["candidate_entity_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index("ix_resolution_hypothesis_candidate_entity_id", table_name="resolution_hypotheses")
    op.drop_index("ix_resolution_hypothesis_mention_id", table_name="resolution_hypotheses")
    op.drop_table("resolution_hypotheses")

    op.drop_index("ix_audit_event_created_at", table_name="audit_events")
    op.drop_index("ix_audit_event_case_id", table_name="audit_events")
    op.drop_table("audit_events")

    op.drop_table("confidence_assessments")
    op.drop_table("evidence_links")

    op.drop_index("ix_claim_case_id", table_name="claims")
    op.drop_table("claims")

    op.drop_index("ix_entity_case_id", table_name="entities")
    op.drop_table("entities")

    op.drop_table("mentions")

    op.drop_index("ix_source_document_sha256", table_name="source_documents")
    op.drop_index("ix_source_document_case_id", table_name="source_documents")
    op.drop_table("source_documents")

    op.drop_table("cases")

    op.execute(sa.text(f"DROP TYPE IF EXISTS {_RESOLUTION_ENUM}"))
    op.execute(sa.text(f"DROP TYPE IF EXISTS {_CONFIDENCE_ENUM}"))
