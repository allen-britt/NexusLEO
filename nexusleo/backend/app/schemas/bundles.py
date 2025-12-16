"""Bundle schemas for orchestration and export."""
from __future__ import annotations

from datetime import datetime
from typing import Any, Dict, List, Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict

from .claim import ClaimOut
from .ingest import IngestResult


class RunCaseRequest(BaseModel):
    document_id: UUID
    actor: Optional[str] = None


class RunCaseResponse(BaseModel):
    ingest_result: IngestResult
    claims: List[ClaimOut]


class CaseExportCase(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    name: Optional[str] = None
    created_at: datetime


class CaseExportDocument(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    type: str
    sha256: str
    created_at: datetime
    metadata_json: Dict[str, Any]


class CaseExportAuditEvent(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    case_id: UUID
    actor: str
    action: str
    tool: str
    tool_version: str
    input_refs_json: Dict[str, Any]
    output_refs_json: Dict[str, Any]
    created_at: datetime


class CaseExportBundle(BaseModel):
    case: CaseExportCase
    documents: List[CaseExportDocument]
    claims: List[ClaimOut]
    audit_events: List[CaseExportAuditEvent]
