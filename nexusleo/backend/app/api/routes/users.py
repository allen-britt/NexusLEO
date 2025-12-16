"""User routes."""
from __future__ import annotations

from fastapi import APIRouter, Body, Depends
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import User
from app.schemas.user import UserCreate, UserOut

router = APIRouter()


@router.post("/users", response_model=UserOut)
def create_user(
    payload: UserCreate = Body(...),
    db: Session = Depends(get_db),
) -> UserOut:
    user = User(display_name=payload.display_name, badge_id=payload.badge_id)
    db.add(user)
    db.commit()
    db.refresh(user)
    return UserOut.model_validate(user)
