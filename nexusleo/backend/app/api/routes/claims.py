"""Claim routes."""
from __future__ import annotations

from typing import List
from uuid import UUID

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.db import get_db
from app.models import AuditEvent, Claim, ConfidenceAssessment, EvidenceLink, Mention
from app.schemas import ClaimOut, ConfidenceOut, EvidenceOut, MentionOut

router = APIRouter()


@router.get("/cases/{case_id}/claims", response_model=List[ClaimOut])
def list_claims(
    case_id: UUID,
    limit: int = Query(100, ge=0),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
) -> List[ClaimOut]:
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
        .offset(offset)
        .limit(limit)
        .all()
    )

    out: list[ClaimOut] = []
    for claim in claims:
        confidence = (
            db.query(ConfidenceAssessment)
            .filter(ConfidenceAssessment.claim_id == claim.id)
            .one_or_none()
        )
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
