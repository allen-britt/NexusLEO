"""Document routes."""
from __future__ import annotations

import hashlib
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import Case, SourceDocument
from app.schemas import DocumentCreate, DocumentOut

router = APIRouter()


@router.post("/cases/{case_id}/documents", response_model=DocumentOut)
def create_document(
    case_id: UUID,
    payload: DocumentCreate = Body(
        ...,  # noqa: B008
        examples={
            "transcript": {
                "summary": "Transcript",
                "value": {
                    "type": "TRANSCRIPT",
                    "text": "A: John Smith met Jane Doe in Baltimore.\nB: John Smith met Jane Doe in Baltimore.",
                    "metadata": {"source": "demo"},
                },
            }
        },
    ),
    db: Session = Depends(get_db),
) -> DocumentOut:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    sha256 = hashlib.sha256(payload.text.encode("utf-8")).hexdigest()
    existing = (
        db.query(SourceDocument)
        .filter(SourceDocument.case_id == case_id, SourceDocument.sha256 == sha256)
        .one_or_none()
    )
    if existing is not None:
        return DocumentOut.model_validate(existing)

    doc = SourceDocument(
        case_id=case_id,
        type=payload.type,
        sha256=sha256,
        metadata_json=payload.metadata,
        raw_text=payload.text,
    )
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return DocumentOut.model_validate(doc)
