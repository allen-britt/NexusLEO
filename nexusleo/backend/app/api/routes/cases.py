"""Case routes."""
from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import Case
from app.schemas import CaseCreate, CaseOut

router = APIRouter()


@router.post("/cases", response_model=CaseOut)
def create_case(payload: CaseCreate, db: Session = Depends(get_db)) -> CaseOut:
    case = Case(name=payload.name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)
