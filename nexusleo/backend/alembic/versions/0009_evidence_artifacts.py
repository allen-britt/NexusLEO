from __future__ import annotations

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


revision = "0009_evidence_artifacts"
down_revision = "0008_case_profile_audit"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "evidence_artifacts",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True, server_default=sa.text("gen_random_uuid()")),
        sa.Column("case_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("cases.id", ondelete="CASCADE"), nullable=False),
        sa.Column("kind", sa.String(), nullable=False),
        sa.Column("label", sa.String(), nullable=False),
        sa.Column("uri", sa.String(), nullable=False),
        sa.Column("sha256", sa.String(), nullable=True),
        sa.Column("captured_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("metadata_json", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
    )
    op.create_index("ix_evidence_artifact_case_id", "evidence_artifacts", ["case_id"], unique=False)
    op.create_index("ix_evidence_artifact_created_at", "evidence_artifacts", ["created_at"], unique=False)


def downgrade() -> None:
    op.drop_index("ix_evidence_artifact_created_at", table_name="evidence_artifacts")
    op.drop_index("ix_evidence_artifact_case_id", table_name="evidence_artifacts")
    op.drop_table("evidence_artifacts")
