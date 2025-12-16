"""Case routes."""
from __future__ import annotations

import hashlib

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from uuid import UUID

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import ActivityLogEntry, AuditEvent, Case, Claim, ConfidenceAssessment, EvidenceLink, Mention, SourceDocument
from app.schemas import CaseCreate, CaseOut, ClaimOut, ConfidenceOut, EvidenceOut, MentionOut
from app.schemas.attach_activity import AttachActivityRequest, AttachActivityResponse
from app.schemas.bundles import (
    CaseExportAuditEvent,
    CaseExportBundle,
    CaseExportCase,
    CaseExportDocument,
    RunCaseRequest,
    RunCaseResponse,
)
from app.services.ingest import ingest_document

router = APIRouter()

_TOOL = "nexusleo.case"
_TOOL_VERSION = "0.2.0"


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


@router.post("/cases", response_model=CaseOut)
def create_case(
    payload: CaseCreate = Body(
        ...,  # noqa: B008
        examples={
            "default": {"summary": "Create case", "value": {"name": "Demo Case"}},
            "unnamed": {"summary": "Unnamed case", "value": {}},
        },
    ),
    db: Session = Depends(get_db),
) -> CaseOut:
    case = Case(name=payload.name)
    db.add(case)
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)


@router.post("/cases/{case_id}/attach_activity", response_model=AttachActivityResponse)
def attach_activity(
    case_id: UUID,
    payload: AttachActivityRequest = Body(...),
    db: Session = Depends(get_db),
) -> AttachActivityResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    activity = db.get(ActivityLogEntry, payload.activity_log_entry_id)
    if activity is None:
        raise HTTPException(status_code=404, detail=ErrorToken.ACTIVITY_NOT_FOUND.value)

    mode = payload.mode or "LINK_ONLY"
    actor = payload.actor or "system"

    # Always link the activity to the case.
    activity.case_id = case_id
    db.flush()

    linked = True
    note_document_id: UUID | None = None
    ingest_result = None
    claims: list[ClaimOut] = []
    claim_ids_out: list[str] = []

    if mode == "COPY_NOTE_AND_INGEST":
        if activity.source_document_id is not None:
            origin_doc = db.get(SourceDocument, activity.source_document_id)
            if origin_doc is not None:
                raw_text = origin_doc.raw_text
                sha256 = hashlib.sha256(raw_text.encode("utf-8")).hexdigest()

                existing = (
                    db.query(SourceDocument)
                    .filter(SourceDocument.case_id == case_id, SourceDocument.sha256 == sha256)
                    .one_or_none()
                )
                if existing is None:
                    origin_shift_id = None
                    if isinstance(activity.metadata_json, dict):
                        origin_shift_id = activity.metadata_json.get("shift_id")

                    doc = SourceDocument(
                        case_id=case_id,
                        type="NOTE",
                        sha256=sha256,
                        metadata_json={
                            "source": "attached_activity",
                            "origin_activity_log_entry_id": str(activity.id),
                            "origin_source_document_id": str(origin_doc.id),
                            "origin_shift_id": origin_shift_id,
                        },
                        raw_text=raw_text,
                    )
                    db.add(doc)
                    db.flush()
                else:
                    doc = existing

                note_document_id = doc.id
                ingest_result = ingest_document(db=db, case_id=str(case_id), document_id=str(doc.id), actor=actor)
                claims = _build_claims_out(db, case_id=case_id)
                claim_ids_out = [str(cid) for cid in ingest_result.claim_ids]

    audit = AuditEvent(
        case_id=case_id,
        actor=actor,
        action="activity_attached",
        tool=_TOOL,
        tool_version=_TOOL_VERSION,
        input_refs_json={
            "case_id": str(case_id),
            "activity_log_entry_id": str(activity.id),
            "mode": mode,
        },
        output_refs_json={
            "linked": linked,
            "note_document_id": str(note_document_id) if note_document_id is not None else None,
            "claim_ids": claim_ids_out,
        },
    )
    db.add(audit)
    db.flush()

    db.commit()

    return AttachActivityResponse(
        case_id=case_id,
        activity_log_entry_id=activity.id,
        mode=mode,
        linked=linked,
        note_document_id=note_document_id,
        ingest_result=ingest_result,
        claims=claims,
        audit_event_id=audit.id,
    )


@router.post("/cases/{case_id}/run", response_model=RunCaseResponse)
def run_case(
    case_id: UUID,
    payload: RunCaseRequest = Body(
        ...,  # noqa: B008
        examples={
            "run": {"summary": "Run case ingest", "value": {"document_id": "00000000-0000-0000-0000-000000000000"}},
        },
    ),
    db: Session = Depends(get_db),
) -> RunCaseResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    document = db.get(SourceDocument, payload.document_id)
    if document is None or document.case_id != case_id:
        raise HTTPException(status_code=404, detail=ErrorToken.DOCUMENT_NOT_FOUND.value)

    ingest_result = ingest_document(
        db=db,
        case_id=str(case_id),
        document_id=str(payload.document_id),
        actor=payload.actor,
    )

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

    return RunCaseResponse(ingest_result=ingest_result, claims=out)


@router.get(
    "/cases/{case_id}/export",
    response_model=CaseExportBundle,
    responses={
        200: {
            "content": {
                "application/json": {
                    "example": {
                        "case": {
                            "id": "00000000-0000-0000-0000-000000000000",
                            "name": "Demo Case",
                            "created_at": "2025-01-01T00:00:00Z",
                        },
                        "documents": [],
                        "claims": [],
                        "audit_events": [],
                    }
                }
            }
        }
    },
)
def export_case(
    case_id: UUID,
    limit: int = Query(100, ge=0),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> CaseExportBundle:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    documents = (
        db.query(SourceDocument)
        .filter(SourceDocument.case_id == case_id)
        .order_by(SourceDocument.created_at.asc(), SourceDocument.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    audit_events = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    audit_ids = [ev.id for ev in audit_events]
    claims = (
        db.query(Claim)
        .filter(Claim.case_id == case_id)
        .order_by(Claim.created_at.asc(), Claim.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )

    claims_out: list[ClaimOut] = []
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

        claims_out.append(
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

    return CaseExportBundle(
        case=CaseExportCase.model_validate(case),
        documents=[CaseExportDocument.model_validate(d) for d in documents],
        claims=claims_out,
        audit_events=[CaseExportAuditEvent.model_validate(a) for a in audit_events],
    )
