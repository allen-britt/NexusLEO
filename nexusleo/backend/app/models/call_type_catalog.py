"""Call type catalog model."""
from __future__ import annotations

from sqlalchemy import Boolean, Column, DateTime, Index, String, Text
from sqlalchemy.dialects.postgresql import JSONB, UUID
from sqlalchemy.sql import func, text
from sqlalchemy.orm import relationship

from .base import Base


class CallTypeCatalog(Base):
    """Reference catalog for call types (e.g., CAD/dispatch codes)."""

    __tablename__ = "call_type_catalog"
    __table_args__ = (
        Index("ix_call_type_catalog_jurisdiction", "jurisdiction"),
        Index("ix_call_type_catalog_code", "code"),
        Index("ix_call_type_catalog_active", "active"),
    )

    id = Column(UUID(as_uuid=True), primary_key=True, server_default=func.gen_random_uuid())
    jurisdiction = Column(String, nullable=False)
    system = Column(String, nullable=False)
    code = Column(String, nullable=False)
    label = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    tags_json = Column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))
    active = Column(Boolean, nullable=False, server_default=text("true"))
    created_at = Column(DateTime(timezone=True), nullable=False, server_default=func.now())

    selections = relationship("CaseCodeSelection", back_populates="call_type_catalog")
