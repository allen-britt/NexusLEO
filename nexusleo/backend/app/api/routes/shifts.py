"""Shift and activity logging routes."""
from __future__ import annotations

import hashlib
from datetime import datetime, timezone
from typing import List
from uuid import UUID

from fastapi import APIRouter, Body, Depends, HTTPException
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import (
    ActivityLogEntry,
    AuditEvent,
    Case,
    Claim,
    ConfidenceAssessment,
    EvidenceLink,
    Mention,
    ShiftSession,
    SourceDocument,
    User,
)
from app.schemas.activity import ActivityLogCreate, ActivityLogOut
from app.schemas.claim import ClaimOut, ConfidenceOut, EvidenceOut
from app.schemas.document import DocumentOut
from app.schemas.shift import ShiftEndResponse, ShiftStartRequest, ShiftStartResponse
from app.schemas.shift_note import ShiftLogNoteCreate, ShiftLogNoteOut
from app.schemas.mention import MentionOut
from app.services.ingest import ingest_document

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


def _build_claims_out(db: Session, *, case_id: UUID) -> list[ClaimOut]:
    audit_ids = [
        row[0]
        for row in (
            db.query(AuditEvent.id)
            .filter(AuditEvent.case_id == case_id)
            .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
            .all()
        )
    ]

    claims = (
        db.query(Claim)
        .filter(Claim.case_id == case_id)
        .order_by(Claim.created_at.asc(), Claim.id.asc())
        .all()
    )

    out: list[ClaimOut] = []
    for claim in claims:
        confidence = db.query(ConfidenceAssessment).filter(ConfidenceAssessment.claim_id == claim.id).one_or_none()
        confidence_out = None
        if confidence is not None:
            confidence_out = ConfidenceOut(
                level=str(confidence.level.value if hasattr(confidence.level, "value") else confidence.level),
                rubric_version=confidence.rubric_version,
                factors_json=confidence.factors_json,
                rationale_text=confidence.rationale_text,
            )

        links = (
            db.query(EvidenceLink, Mention)
            .join(Mention, EvidenceLink.mention_id == Mention.id)
            .filter(EvidenceLink.claim_id == claim.id)
            .order_by(Mention.id.asc(), EvidenceLink.id.asc())
            .all()
        )

        evidence: list[EvidenceOut] = []
        for link, mention in links:
            evidence.append(
                EvidenceOut(
                    evidence_link_id=link.id,
                    weight=link.weight,
                    notes=link.notes,
                    mention=MentionOut(
                        id=mention.id,
                        document_id=mention.document_id,
                        text=mention.text,
                        start=mention.start,
                        end=mention.end,
                        speaker=mention.speaker,
                        timestamp=mention.timestamp,
                        language=mention.language,
                        entity_type_guess=mention.entity_type_guess,
                    ),
                    document_id=mention.document_id,
                )
            )

        out.append(
            ClaimOut(
                id=claim.id,
                case_id=claim.case_id,
                claim_type=claim.claim_type,
                predicate=claim.predicate,
                text=claim.text,
                subject_entity_id=claim.subject_entity_id,
                object_entity_id=claim.object_entity_id,
                created_at=claim.created_at,
                confidence=confidence_out,
                evidence=evidence,
                audit_event_ids=audit_ids,
            )
        )

    return out


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
        source_document_id=entry.source_document_id,
        occurred_at=entry.occurred_at,
        entry_type=entry.entry_type,
        text=entry.text,
        metadata_json=entry.metadata_json,
        created_at=entry.created_at,
        timeline_item_type="NOTE_CREATED" if entry.source_document_id is not None else "ACTIVITY_LOGGED",
    )


@router.post("/shifts/{shift_id}/log_note", response_model=ShiftLogNoteOut)
def log_note(
    shift_id: UUID,
    payload: ShiftLogNoteCreate = Body(...),
    db: Session = Depends(get_db),
) -> ShiftLogNoteOut:
    shift = db.get(ShiftSession, shift_id)
    if shift is None:
        raise HTTPException(status_code=404, detail=ErrorToken.SHIFT_NOT_FOUND.value)

    case_id = payload.case_id
    if case_id is not None:
        case = db.get(Case, case_id)
        if case is None:
            raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)
    else:
        bucket_name = f"Shift {shift_id} Notes"
        existing_bucket = db.query(Case).filter(Case.name == bucket_name).order_by(Case.id.asc()).first()
        if existing_bucket is None:
            existing_bucket = Case(name=bucket_name)
            db.add(existing_bucket)
            db.flush()
        case_id = existing_bucket.id

    occurred_at = payload.occurred_at or datetime.now(timezone.utc)

    entry = ActivityLogEntry(
        shift_id=shift.id,
        case_id=case_id,
        occurred_at=occurred_at,
        entry_type=payload.entry_type,
        text=payload.text,
        metadata_json={"source": "shift_log_note"},
    )
    db.add(entry)
    db.flush()

    sha256 = hashlib.sha256(payload.text.encode("utf-8")).hexdigest()
    existing_doc = (
        db.query(SourceDocument)
        .filter(SourceDocument.case_id == case_id, SourceDocument.sha256 == sha256)
        .one_or_none()
    )
    if existing_doc is None:
        doc = SourceDocument(
            case_id=case_id,
            type="NOTE",
            sha256=sha256,
            metadata_json={
                "shift_id": str(shift.id),
                "activity_log_entry_id": str(entry.id),
                "entry_type": entry.entry_type,
                "occurred_at": entry.occurred_at.isoformat(),
                "source": "shift_log_note",
            },
            raw_text=payload.text,
        )
        db.add(doc)
        db.flush()
    else:
        doc = existing_doc

    entry.source_document_id = doc.id
    db.flush()

    user = db.get(User, shift.user_id)
    actor = payload.actor or (user.display_name if user is not None else "system")

    ingest_result = ingest_document(db=db, case_id=str(case_id), document_id=str(doc.id), actor=actor)
    claims_out = _build_claims_out(db, case_id=case_id)

    _audit(
        db,
        actor=actor,
        action="shift_note_logged",
        case_id=case_id,
        input_refs={
            "shift_id": str(shift.id),
            "user_id": str(shift.user_id),
            "case_id": str(case_id),
            "activity_log_entry_id": str(entry.id),
            "document_id": str(doc.id),
            "sha256": sha256,
        },
        output_refs={"claim_ids": [str(cid) for cid in ingest_result.claim_ids]},
    )

    db.commit()
    db.refresh(entry)
    db.refresh(doc)

    activity_out = ActivityLogOut(
        id=entry.id,
        shift_id=entry.shift_id,
        case_id=entry.case_id,
        source_document_id=entry.source_document_id,
        occurred_at=entry.occurred_at,
        entry_type=entry.entry_type,
        text=entry.text,
        metadata_json=entry.metadata_json,
        created_at=entry.created_at,
        timeline_item_type="NOTE_CREATED",
    )

    return ShiftLogNoteOut(
        activity_log_entry=activity_out,
        document=DocumentOut.model_validate(doc),
        ingest_result=ingest_result,
        claims=claims_out,
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
                source_document_id=e.source_document_id,
                occurred_at=e.occurred_at,
                entry_type=e.entry_type,
                text=e.text,
                metadata_json=e.metadata_json,
                created_at=e.created_at,
                timeline_item_type="NOTE_CREATED" if e.source_document_id is not None else "ACTIVITY_LOGGED",
            )
        )
    return out
