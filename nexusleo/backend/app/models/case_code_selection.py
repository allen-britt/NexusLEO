"""Case code selection model."""
from __future__ import annotations

from sqlalchemy import CheckConstraint, Column, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from .base import Base


class CaseCodeSelection(Base):
    """Selection of a catalog item (code or call type) attached to a case."""

    __tablename__ = "case_code_selections"
    __table_args__ = (
        CheckConstraint("catalog_type in ('CODE','CALL_TYPE')", name="catalog_type_allowed"),
        CheckConstraint(
            "(catalog_type = 'CODE' and code_catalog_id is not null and call_type_catalog_id is null)"
            " or (catalog_type = 'CALL_TYPE' and call_type_catalog_id is not null and code_catalog_id is null)",
            name="catalog_reference_match",
        ),
        Index("ix_case_code_selection_case_id", "case_id"),
        Index("ix_case_code_selection_selected_at", "selected_at"),
        Index(
            "uq_case_code_selection_code",
            "case_id",
            "code_catalog_id",
            unique=True,
            postgresql_where=text("catalog_type = 'CODE'"),
        ),
        Index(
            "uq_case_code_selection_call_type",
            "case_id",
            "call_type_catalog_id",
            unique=True,
            postgresql_where=text("catalog_type = 'CALL_TYPE'"),
        ),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id", ondelete="CASCADE"), nullable=False)
    catalog_type = Column(String, nullable=False)
    code_catalog_id = Column(UUID(as_uuid=True), ForeignKey("code_catalog.id", ondelete="CASCADE"), nullable=True)
    call_type_catalog_id = Column(UUID(as_uuid=True), ForeignKey("call_type_catalog.id", ondelete="CASCADE"), nullable=True)
    selected_by = Column(String, nullable=False, server_default="system")
    selected_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    note = Column(Text, nullable=True)

    code_catalog = relationship("CodeCatalog", back_populates="selections")
    call_type_catalog = relationship("CallTypeCatalog", back_populates="selections")
