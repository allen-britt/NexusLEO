"""Deterministic procedural guidance builder.

This module is strictly rule-based and produces neutral procedural considerations
based on existing case data.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from uuid import UUID, uuid5

from sqlalchemy.orm import Session

from app.models import ActivityLogEntry, AuditEvent, Case, Claim, ConfidenceAssessment, SourceDocument
from app.schemas.guidance import CaseGuidanceResponse, GuidanceItem

_NAMESPACE = UUID("00000000-0000-0000-0000-000000000701")

_TIME_PATTERN = re.compile(r"\b(\d{4}-\d{2}-\d{2}|\d{1,2}:\d{2})\b")
_LOCATION_PATTERN = re.compile(r"\b(street|st\.|avenue|ave\.|road|rd\.|boulevard|blvd\.|lane|ln\.|drive|dr\.|block)\b", re.IGNORECASE)


def _max_dt(values: list[datetime]) -> datetime:
    filtered = [v for v in values if isinstance(v, datetime)]
    if not filtered:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    out = max(filtered)
    if out.tzinfo is None:
        out = out.replace(tzinfo=timezone.utc)
    return out


def _stable_id(*parts: str) -> UUID:
    return uuid5(_NAMESPACE, "|".join(parts))


def build_case_guidance(db: Session, *, case_id: UUID) -> CaseGuidanceResponse:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise LookupError("case_not_found")

    docs = (
        db.query(SourceDocument)
        .filter(SourceDocument.case_id == case_id)
        .order_by(SourceDocument.created_at.asc(), SourceDocument.id.asc())
        .all()
    )
    activities = (
        db.query(ActivityLogEntry)
        .filter(ActivityLogEntry.case_id == case_id)
        .order_by(ActivityLogEntry.created_at.asc(), ActivityLogEntry.id.asc())
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

    generated_at = _max_dt(
        [case.created_at]
        + [d.created_at for d in docs]
        + [a.created_at for a in activities]
        + [c.created_at for c in claims]
        + [a.created_at for a in audits]
    )

    raw_texts: list[str] = []
    for d in docs:
        if d.raw_text:
            raw_texts.append(d.raw_text)
    for a in activities:
        if a.text:
            raw_texts.append(a.text)
    combined = "\n".join(raw_texts)

    has_time = bool(_TIME_PATTERN.search(combined))
    has_location = bool(_LOCATION_PATTERN.search(combined))

    item_rows: list[tuple[str, str, UUID, GuidanceItem]] = []

    if docs or activities:
        statement = "Procedural consideration: use consistent identifiers for parties across notes and activity logs."
        gid = _stable_id("identity", statement)
        related: list[UUID] = [d.id for d in docs[:3]] + [a.id for a in activities[:3]]
        item_rows.append(
            (
                "identity",
                statement,
                gid,
                GuidanceItem(
                    id=gid,
                    category="identity",
                    statement=statement,
                    source="timeline",
                    confidence="MODERATE",
                    related_ids=related,
                ),
            )
        )

    if docs or activities:
        if not has_time or not has_location:
            parts: list[str] = []
            if not has_time:
                parts.append("time")
            if not has_location:
                parts.append("location")
            missing = " and ".join(parts)
            statement = f"Procedural consideration: {missing} is commonly documented when available; record it consistently."
            gid = _stable_id("documentation", statement)
            related = [d.id for d in docs[:3]] + [a.id for a in activities[:3]]
            item_rows.append(
                (
                    "documentation",
                    statement,
                    gid,
                    GuidanceItem(
                        id=gid,
                        category="documentation",
                        statement=statement,
                        source="timeline",
                        confidence="LOW",
                        related_ids=related,
                    ),
                )
            )

    if docs:
        statement = "Procedural consideration: attribute statements to sources and keep observations separate from attributed statements."
        gid = _stable_id("reporting", statement)
        related = [d.id for d in docs[:3]]
        item_rows.append(
            (
                "reporting",
                statement,
                gid,
                GuidanceItem(
                    id=gid,
                    category="reporting",
                    statement=statement,
                    source="document",
                    confidence="MODERATE",
                    related_ids=related,
                ),
            )
        )

    if claims:
        statement = "Procedural consideration: align claim-derived references with supporting notes and timeline entries for consistency."
        gid = _stable_id("evidence", statement)
        related = [c.id for c in claims[:3]]

        conf = db.query(ConfidenceAssessment).filter(ConfidenceAssessment.claim_id == claims[0].id).one_or_none()
        level = "LOW"
        if conf is not None:
            raw = str(conf.level.value if hasattr(conf.level, "value") else conf.level)
            if raw == "HIGH":
                level = "HIGH"
            elif raw in {"MODERATE", "MEDIUM"}:
                level = "MODERATE"

        item_rows.append(
            (
                "evidence",
                statement,
                gid,
                GuidanceItem(
                    id=gid,
                    category="evidence",
                    statement=statement,
                    source="claim",
                    confidence=level,
                    related_ids=related,
                ),
            )
        )

    item_rows.sort(key=lambda row: (row[0], row[1], str(row[2])))
    items = [row[3] for row in item_rows]

    return CaseGuidanceResponse(case_id=case.id, generated_at=generated_at, items=items)
