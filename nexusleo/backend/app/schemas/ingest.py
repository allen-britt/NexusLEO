"""Ingest request/response schemas."""
from __future__ import annotations

from typing import List, Optional
from uuid import UUID

from pydantic import BaseModel


class IngestRequest(BaseModel):
    document_id: UUID
    actor: Optional[str] = None


class IngestResult(BaseModel):
    document_id: UUID
    mentions_created: int
    entities_created: int
    claims_created: int
    evidence_links_created: int
    confidence_created: int
    audit_events_created: int
    claim_ids: List[UUID]
