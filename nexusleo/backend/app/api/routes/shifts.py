"""Shift and activity logging routes."""
from __future__ import annotations

from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import ActivityLogEntry, AuditEvent, Case, ShiftSession, User
from app.schemas.activity import ActivityLogCreate, ActivityLogOut
from app.schemas.shift import ShiftEndResponse, ShiftStartRequest, ShiftStartResponse

router = APIRouter()

_TOOL = "nexusleo.shift"
_TOOL_VERSION = "0.1.0"


def _audit(
    db: Session,
    *,
    actor: str,
    action: str,
    case_id: UUID | None,
    input_refs: dict,
    output_refs: dict,
) -> None:
    db.add(
        AuditEvent(
            case_id=case_id,
            actor=actor,
            action=action,
            tool=_TOOL,
            tool_version=_TOOL_VERSION,
            input_refs_json=input_refs,
            output_refs_json=output_refs,
        )
    )


@router.post("/shifts/start", response_model=ShiftStartResponse)
def start_shift(
    payload: ShiftStartRequest = Body(...),
    db: Session = Depends(get_db),
) -> ShiftStartResponse:
    user = db.get(User, payload.user_id)
    if user is None:
        raise HTTPException(status_code=404, detail=ErrorToken.USER_NOT_FOUND.value)

    shift = ShiftSession(user_id=user.id, device_id=payload.device_id)
    db.add(shift)
    db.flush()

    _audit(
        db,
        actor=user.display_name,
        action="shift_started",
        case_id=None,
        input_refs={"shift_id": str(shift.id), "user_id": str(user.id), "device_id": payload.device_id},
        output_refs={},
    )

    db.commit()
    return ShiftStartResponse(shift_id=shift.id)


@router.post("/shifts/{shift_id}/end", response_model=ShiftEndResponse)
def end_shift(shift_id: UUID, db: Session = Depends(get_db)) -> ShiftEndResponse:
    shift = db.get(ShiftSession, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail=ErrorToken.SHIFT_NOT_FOUND.value)

    if shift.ended_at is None:
        shift.ended_at = datetime.now(timezone.utc)

    user = db.get(User, shift.user_id)
    actor = user.display_name if user is not None else "system"

    _audit(
        db,
        actor=actor,
        action="shift_ended",
        case_id=None,
        input_refs={"shift_id": str(shift.id), "user_id": str(shift.user_id)},
        output_refs={"ended_at": shift.ended_at.isoformat()},
    )

    db.commit()
    return ShiftEndResponse(shift_id=shift.id, ended_at=shift.ended_at)


@router.post("/shifts/{shift_id}/log", response_model=ActivityLogOut)
def log_activity(
    shift_id: UUID,
    payload: ActivityLogCreate = Body(...),
    db: Session = Depends(get_db),
) -> ActivityLogOut:
    shift = db.get(ShiftSession, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail=ErrorToken.SHIFT_NOT_FOUND.value)

    case_id = payload.case_id
    if case_id is not None:
        case = db.get(Case, case_id)
        if case is None:
            raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    occurred_at = payload.occurred_at or datetime.now(timezone.utc)

    entry = ActivityLogEntry(
        shift_id=shift.id,
        case_id=case_id,
        occurred_at=occurred_at,
        entry_type=payload.entry_type,
        text=payload.text,
        metadata_json=payload.metadata,
    )
    db.add(entry)
    db.flush()

    user = db.get(User, shift.user_id)
    actor = user.display_name if user is not None else "system"

    _audit(
        db,
        actor=actor,
        action="activity_logged",
        case_id=case_id,
        input_refs={
            "shift_id": str(shift.id),
            "user_id": str(shift.user_id),
            "case_id": str(case_id) if case_id is not None else None,
            "entry_id": str(entry.id),
        },
        output_refs={},
    )

    db.commit()
    db.refresh(entry)
    return ActivityLogOut(
        id=entry.id,
        shift_id=entry.shift_id,
        case_id=entry.case_id,
        occurred_at=entry.occurred_at,
        entry_type=entry.entry_type,
        text=entry.text,
        metadata_json=entry.metadata_json,
        created_at=entry.created_at,
    )


@router.get("/shifts/{shift_id}/timeline", response_model=List[ActivityLogOut])
def timeline(shift_id: UUID, db: Session = Depends(get_db)) -> List[ActivityLogOut]:
    shift = db.get(ShiftSession, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail=ErrorToken.SHIFT_NOT_FOUND.value)

    entries = (
        db.query(ActivityLogEntry)
        .filter(ActivityLogEntry.shift_id == shift_id)
        .order_by(ActivityLogEntry.occurred_at.asc(), ActivityLogEntry.created_at.asc(), ActivityLogEntry.id.asc())
        .all()
    )

    out: list[ActivityLogOut] = []
    for e in entries:
        out.append(
            ActivityLogOut(
                id=e.id,
                shift_id=e.shift_id,
                case_id=e.case_id,
                occurred_at=e.occurred_at,
                entry_type=e.entry_type,
                text=e.text,
                metadata_json=e.metadata_json,
                created_at=e.created_at,
            )
        )
    return out
