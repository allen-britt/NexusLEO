"""Ingest routes."""
from __future__ import annotations

from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import SourceDocument
from app.schemas import IngestRequest, IngestResult
from app.services.ingest import ingest_document

router = APIRouter()


@router.post("/cases/{case_id}/ingest", response_model=IngestResult)
def ingest(case_id: UUID, payload: IngestRequest, db: Session = Depends(get_db)) -> IngestResult:
    document = db.get(SourceDocument, payload.document_id)
    if document is None or document.case_id != case_id:
        raise HTTPException(status_code=404, detail="document_not_found")

    return ingest_document(
        db=db,
        case_id=str(case_id),
        document_id=str(payload.document_id),
        actor=payload.actor,
    )
