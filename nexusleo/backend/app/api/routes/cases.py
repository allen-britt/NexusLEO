"""Case routes."""
from __future__ import annotations

import hashlib

from fastapi import APIRouter, Body, Depends, HTTPException, Query
from sqlalchemy.orm import Session, joinedload
from uuid import UUID

from app.core.db import get_db
from app.errors import ErrorToken
from app.models import (
    ActivityLogEntry,
    AuditEvent,
    Case,
    Claim,
    CaseCodeSelection,
    ConfidenceAssessment,
    EvidenceArtifact,
    EvidenceLink,
    Mention,
    ShiftSession,
    SourceDocument,
)
from app.schemas import (
    CaseCreate,
    CaseOut,
    ClaimOut,
    ConfidenceOut,
    EvidenceOut,
    MentionOut,
    CaseStateContextIn,
    ObservedFactsIn,
)
from app.schemas.artifact import ArtifactCreateIn, ArtifactOut
from app.schemas.attach_activity import AttachActivityRequest, AttachActivityResponse
from app.schemas.case_timeline import (
    ActivityMini,
    ArtifactMini,
    AuditMini,
    CaseTimelineItem,
    ClaimMini,
    DocumentMini,
    CodeSelectionMini,
)
from app.schemas.bundles import (
    CaseExportAuditEvent,
    CaseExportBundle,
    CaseExportCase,
    CaseExportDocument,
    RunCaseRequest,
    RunCaseResponse,
)
from app.schemas.guidance import CaseGuidanceResponse
from app.schemas.profile import SetCaseProfileRequest
from app.schemas.report_draft import ReportDraftOut
from app.policy.profiles import get_profile
from app.services.guidance import build_case_guidance
from app.services.ingest import ingest_document
from app.services.report_draft import build_report_draft

router = APIRouter()

_TOOL = "nexusleo.case"
_TOOL_VERSION = "0.2.0"

_PROFILE_TOOL = "nexusleo.profile"
_PROFILE_TOOL_VERSION = "0.1.0"

_INGEST_TOOL = "nexusleo.ingest"
_INGEST_TOOL_VERSION = "0.1.0"


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


@router.post("/cases/{case_id}/state_context")
def set_case_state_context(
    case_id: UUID,
    payload: CaseStateContextIn = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    case.state_context_json = payload.state_context
    db.commit()
    return {"case_id": str(case_id), "state_context": case.state_context_json}


@router.post("/cases/{case_id}/observed_facts")
def set_case_observed_facts(
    case_id: UUID,
    payload: ObservedFactsIn = Body(...),
    db: Session = Depends(get_db),
) -> dict:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    case.observed_facts_json = payload.observed_facts
    db.commit()
    return {"case_id": str(case_id), "observed_facts": case.observed_facts_json}


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


@router.post("/cases/{case_id}/artifacts", response_model=ArtifactOut)
def create_case_artifact(
    case_id: UUID,
    payload: ArtifactCreateIn = Body(...),
    db: Session = Depends(get_db),
) -> ArtifactOut:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    actor = payload.actor or "system"

    artifact = EvidenceArtifact(
        case_id=case_id,
        kind=payload.kind,
        label=payload.label,
        uri=payload.uri,
        sha256=payload.sha256,
        captured_at=payload.captured_at,
        metadata_json=payload.metadata,
    )
    db.add(artifact)
    db.flush()

    audit = AuditEvent(
        case_id=case_id,
        actor=actor,
        action="artifact_added",
        tool=_INGEST_TOOL,
        tool_version=_INGEST_TOOL_VERSION,
        input_refs_json={"case_id": str(case_id)},
        output_refs_json={"artifact_id": str(artifact.id)},
    )
    db.add(audit)

    db.commit()
    db.refresh(artifact)
    return ArtifactOut.model_validate(artifact)


@router.get("/cases/{case_id}/artifacts", response_model=list[ArtifactOut])
def list_case_artifacts(
    case_id: UUID,
    limit: int = Query(100, ge=0),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[ArtifactOut]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    artifacts = (
        db.query(EvidenceArtifact)
        .filter(EvidenceArtifact.case_id == case_id)
        .order_by(EvidenceArtifact.created_at.asc(), EvidenceArtifact.id.asc())
        .offset(offset)
        .limit(limit)
        .all()
    )
    return [ArtifactOut.model_validate(a) for a in artifacts]


@router.get("/cases/{case_id}/timeline", response_model=list[CaseTimelineItem])
def case_timeline(
    case_id: UUID,
    limit: int = Query(100, ge=0, le=500),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> list[CaseTimelineItem]:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    docs = (
        db.query(SourceDocument)
        .filter(SourceDocument.case_id == case_id)
        .order_by(SourceDocument.created_at.asc(), SourceDocument.id.asc())
        .all()
    )
    audits = (
        db.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
        .all()
    )
    claims = (
        db.query(Claim)
        .filter(Claim.case_id == case_id)
        .order_by(Claim.created_at.asc(), Claim.id.asc())
        .all()
    )
    activities = (
        db.query(ActivityLogEntry)
        .filter(ActivityLogEntry.case_id == case_id)
        .order_by(ActivityLogEntry.created_at.asc(), ActivityLogEntry.id.asc())
        .all()
    )

    artifacts = (
        db.query(EvidenceArtifact)
        .filter(EvidenceArtifact.case_id == case_id)
        .order_by(EvidenceArtifact.created_at.asc(), EvidenceArtifact.id.asc())
        .all()
    )

    selections = (
        db.query(CaseCodeSelection)
        .options(joinedload(CaseCodeSelection.code_catalog), joinedload(CaseCodeSelection.call_type_catalog))
        .filter(CaseCodeSelection.case_id == case_id)
        .order_by(
            CaseCodeSelection.selected_at.asc(),
            CaseCodeSelection.catalog_type.asc(),
            CaseCodeSelection.code_catalog_id.asc().nullsfirst(),
            CaseCodeSelection.call_type_catalog_id.asc().nullsfirst(),
            CaseCodeSelection.id.asc(),
        )
        .all()
    )

    items: list[tuple] = []

    for d in docs:
        items.append(
            (
                d.created_at,
                "DOCUMENT_ADDED",
                str(d.id),
                CaseTimelineItem(
                    ts=d.created_at,
                    item_type="DOCUMENT_ADDED",
                    document=DocumentMini(document_id=d.id, document_type=d.type, sha256=d.sha256),
                ),
            )
        )

    for a in audits:
        items.append(
            (
                a.created_at,
                "AUDIT_EVENT",
                str(a.id),
                CaseTimelineItem(
                    ts=a.created_at,
                    item_type="AUDIT_EVENT",
                    audit=AuditMini(
                        audit_event_id=a.id,
                        action=a.action,
                        actor=a.actor,
                        tool=a.tool,
                        tool_version=a.tool_version,
                    ),
                ),
            )
        )

    for sel in selections:
        code = sel.code_catalog
        call_type = sel.call_type_catalog
        label = code.label if code is not None else call_type.label if call_type is not None else ""
        code_value = code.code if code is not None else call_type.code if call_type is not None else ""
        items.append(
            (
                sel.selected_at,
                "CODE_SELECTED",
                str(sel.id),
                CaseTimelineItem(
                    ts=sel.selected_at,
                    item_type="CODE_SELECTED",
                    code_selection=CodeSelectionMini(
                        selection_id=sel.id,
                        catalog_type=sel.catalog_type,
                        code=code_value,
                        label=label,
                    ),
                ),
            )
        )

    for c in claims:
        confidence = db.query(ConfidenceAssessment).filter(ConfidenceAssessment.claim_id == c.id).one_or_none()
        level = None
        if confidence is not None:
            level = str(confidence.level.value if hasattr(confidence.level, "value") else confidence.level)
        items.append(
            (
                c.created_at,
                "CLAIM_CREATED",
                str(c.id),
                CaseTimelineItem(
                    ts=c.created_at,
                    item_type="CLAIM_CREATED",
                    claim=ClaimMini(claim_id=c.id, predicate=c.predicate, text=c.text, confidence_level=level),
                ),
            )
        )

    for act in activities:
        shift = db.get(ShiftSession, act.shift_id)
        officer_user_id = shift.user_id if shift is not None else None
        items.append(
            (
                act.created_at,
                "ACTIVITY_ATTACHED",
                str(act.id),
                CaseTimelineItem(
                    ts=act.created_at,
                    item_type="ACTIVITY_ATTACHED",
                    activity=ActivityMini(
                        activity_id=act.id,
                        shift_id=act.shift_id,
                        officer_user_id=officer_user_id,
                        entry_type=act.entry_type,
                        text=act.text,
                        source_document_id=act.source_document_id,
                    ),
                ),
            )
        )

    for art in artifacts:
        ts = art.captured_at or art.created_at
        items.append(
            (
                ts,
                "ARTIFACT_ADDED",
                str(art.id),
                CaseTimelineItem(
                    ts=ts,
                    item_type="ARTIFACT_ADDED",
                    artifact=ArtifactMini(
                        artifact_id=art.id,
                        kind=art.kind,
                        label=art.label,
                        sha256=art.sha256,
                        captured_at=art.captured_at,
                    ),
                ),
            )
        )

    items.sort(key=lambda row: (row[0], row[1], row[2]))
    sliced = items[offset : offset + limit]
    return [row[3] for row in sliced]


@router.get("/cases/{case_id}/guidance", response_model=CaseGuidanceResponse)
def case_guidance(
    case_id: UUID,
    db: Session = Depends(get_db),
) -> CaseGuidanceResponse:
    try:
        return build_case_guidance(db=db, case_id=case_id)
    except LookupError:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)


@router.get("/cases/{case_id}/report_draft", response_model=ReportDraftOut)
def case_report_draft(
    case_id: UUID,
    db: Session = Depends(get_db),
) -> ReportDraftOut:
    try:
        return build_report_draft(db=db, case_id=case_id)
    except LookupError:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)


@router.post("/cases/{case_id}/profile", response_model=CaseOut)
def set_case_profile(
    case_id: UUID,
    payload: SetCaseProfileRequest = Body(...),
    db: Session = Depends(get_db),
) -> CaseOut:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise HTTPException(status_code=404, detail=ErrorToken.CASE_NOT_FOUND.value)

    prof = get_profile(payload.profile_id)
    if prof is None:
        raise HTTPException(status_code=404, detail=ErrorToken.PROFILE_NOT_FOUND.value)

    actor = payload.actor or "system"
    case.profile_id = prof.profile_id
    db.flush()

    audit = AuditEvent(
        case_id=case_id,
        actor=actor,
        action="case_profile_set",
        tool=_PROFILE_TOOL,
        tool_version=_PROFILE_TOOL_VERSION,
        input_refs_json={"case_id": str(case_id), "profile_id": prof.profile_id},
        output_refs_json={"profile_id": prof.profile_id},
    )
    db.add(audit)
    db.commit()
    db.refresh(case)
    return CaseOut.model_validate(case)


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
