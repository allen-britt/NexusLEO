"""add profile_id to cases

Revision ID: 0007_case_profile_id
Revises: 0006_case_audit_vocab
Create Date: 2025-12-16

"""
from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0007_case_profile_id"
down_revision = "0006_case_audit_vocab"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.add_column("cases", sa.Column("profile_id", sa.String(length=64), nullable=True))
    op.create_index("ix_cases_profile_id", "cases", ["profile_id"])


def downgrade() -> None:
    op.drop_index("ix_cases_profile_id", table_name="cases")
    op.drop_column("cases", "profile_id")
