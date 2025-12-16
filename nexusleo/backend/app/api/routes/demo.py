"""Demo helper routes (non-persistent)."""
from __future__ import annotations

import hashlib
import os

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import Case, SourceDocument
from app.schemas.demo import DemoSeedOut

router = APIRouter()


@router.post(
    "/_demo/seed",
    response_model=DemoSeedOut,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "case_id": "00000000-0000-0000-0000-000000000000",
                        "document_id": "00000000-0000-0000-0000-000000000000",
                    }
                }
            }
        }
    },
)
def demo_seed(db: Session = Depends(get_db)) -> DemoSeedOut:
    env = (os.getenv("ENV") or "").lower()
    if env == "production":
        raise HTTPException(status_code=404, detail=ErrorToken.NOT_AVAILABLE.value)

    case = Case(name="Demo Case")
    db.add(case)
    db.flush()

    text = "A: John Smith met Jane Doe in Baltimore.\nB: John Smith met Jane Doe in Baltimore."
    sha256 = hashlib.sha256(text.encode("utf-8")).hexdigest()

    doc = SourceDocument(
        case_id=case.id,
        type="TRANSCRIPT",
        sha256=sha256,
        metadata_json={"source": "demo"},
        raw_text=text,
    )
    db.add(doc)

    db.commit()
    db.refresh(case)
    db.refresh(doc)

    return DemoSeedOut(case_id=case.id, document_id=doc.id)
