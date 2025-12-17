from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import ActivityLogEntry, AuditEvent, Case, Claim, SourceDocument
from app.schemas import CaseOut
from app.schemas.report_draft import ReportDraftOut, ReportSectionOut, SourceRefOut


@dataclass(frozen=True)
class _DocRow:
    id: UUID
    created_at: datetime
    type: str
    sha256: str


@dataclass(frozen=True)
class _ActivityRow:
    id: UUID
    occurred_at: datetime
    created_at: datetime
    entry_type: str
    text: str


@dataclass(frozen=True)
class _AuditRow:
    id: UUID
    created_at: datetime
    action: str
    actor: str
    tool: str
    tool_version: str


@dataclass(frozen=True)
class _ClaimRow:
    id: UUID
    created_at: datetime
    predicate: str
    text: str


def _utc_now_deterministic() -> datetime:
    return datetime(1970, 1, 1, tzinfo=timezone.utc)


def _md_escape_inline(text: str) -> str:
    return text.replace("\n", " ").strip()


def _build_timeline_items(
    *,
    docs: Iterable[_DocRow],
    audits: Iterable[_AuditRow],
    claims: Iterable[_ClaimRow],
    activities: Iterable[_ActivityRow],
) -> list[tuple[datetime, str, str, str, list[SourceRefOut]]]:
    items: list[tuple[datetime, str, str, str, list[SourceRefOut]]] = []

    for d in docs:
        items.append(
            (
                d.created_at,
                "DOCUMENT_ADDED",
                str(d.id),
                f"- {d.created_at.isoformat()} DOCUMENT_ADDED document_id={d.id} type={_md_escape_inline(d.type)} sha256={_md_escape_inline(d.sha256)}",
                [SourceRefOut(source_type="document", source_id=d.id, ts=d.created_at)],
            )
        )

    for a in audits:
        items.append(
            (
                a.created_at,
                "AUDIT_EVENT",
                str(a.id),
                f"- {a.created_at.isoformat()} AUDIT_EVENT audit_event_id={a.id} action={_md_escape_inline(a.action)} actor={_md_escape_inline(a.actor)} tool={_md_escape_inline(a.tool)} tool_version={_md_escape_inline(a.tool_version)}",
                [SourceRefOut(source_type="audit_event", source_id=a.id, ts=a.created_at)],
            )
        )

    for c in claims:
        items.append(
            (
                c.created_at,
                "CLAIM_CREATED",
                str(c.id),
                f"- {c.created_at.isoformat()} CLAIM_CREATED claim_id={c.id} predicate={_md_escape_inline(c.predicate)} text={_md_escape_inline(c.text)}",
                [SourceRefOut(source_type="claim", source_id=c.id, ts=c.created_at)],
            )
        )

    for act in activities:
        ts = act.occurred_at
        items.append(
            (
                ts,
                "ACTIVITY_ATTACHED",
                str(act.id),
                f"- {ts.isoformat()} ACTIVITY_ATTACHED activity_id={act.id} entry_type={_md_escape_inline(act.entry_type)} text={_md_escape_inline(act.text)}",
                [SourceRefOut(source_type="activity", source_id=act.id, ts=ts)],
            )
        )

    items.sort(key=lambda row: (row[0], row[1], row[2]))
    return items


def _build_claims_grouped(*, claims: Iterable[_ClaimRow]) -> tuple[str, list[SourceRefOut]]:
    rows = sorted([(c.predicate, c.text, str(c.id), c) for c in claims], key=lambda r: (r[0], r[1], r[2]))

    lines: list[str] = []
    refs: list[SourceRefOut] = []
    current_pred: str | None = None

    for predicate, text, _id_str, c in rows:
        if current_pred != predicate:
            current_pred = predicate
            lines.append(f"### {predicate}")
        lines.append(f"- claim_id={c.id} created_at={c.created_at.isoformat()} text={_md_escape_inline(text)}")
        refs.append(SourceRefOut(source_type="claim", source_id=c.id, ts=c.created_at))

    return "\n".join(lines).strip() + ("\n" if lines else ""), refs


def _build_people_locations_vehicles_sections(
    *,
    claims: list[_ClaimRow],
    fallback_refs: list[SourceRefOut],
) -> list[ReportSectionOut]:
    rows = sorted([(c.predicate, c.text, str(c.id), c) for c in claims], key=lambda r: (r[0], r[1], r[2]))
    people_lines: list[str] = []
    vehicle_lines: list[str] = []
    location_lines: list[str] = []

    for predicate, text, _id_str, c in rows:
        line = f"- claim_id={c.id} predicate={_md_escape_inline(predicate)} text={_md_escape_inline(text)}"
        if "PERSON" in predicate or "NAME" in predicate:
            people_lines.append(line)
        if "VEH" in predicate or "PLATE" in predicate:
            vehicle_lines.append(line)
        if "LOC" in predicate or "ADDRESS" in predicate or "CITY" in predicate:
            location_lines.append(line)

    if not people_lines:
        people_lines = ["- (none)\n"]
    if not vehicle_lines:
        vehicle_lines = ["- (none)\n"]
    if not location_lines:
        location_lines = ["- (none)\n"]

    refs = fallback_refs[:1] if fallback_refs else []

    return [
        ReportSectionOut(
            key="people",
            title="People",
            content_markdown=("\n".join(people_lines).strip() + "\n"),
            source_refs=refs,
        ),
        ReportSectionOut(
            key="vehicles",
            title="Vehicles",
            content_markdown=("\n".join(vehicle_lines).strip() + "\n"),
            source_refs=refs,
        ),
        ReportSectionOut(
            key="locations",
            title="Locations",
            content_markdown=("\n".join(location_lines).strip() + "\n"),
            source_refs=refs,
        ),
    ]


def build_report_draft(*, db: Session, case_id: UUID) -> ReportDraftOut:
    case = db.query(Case).filter(Case.id == case_id).first()
    if case is None:
        raise LookupError("case_not_found")

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

    doc_rows = [_DocRow(id=d.id, created_at=d.created_at, type=d.type, sha256=d.sha256) for d in docs]
    audit_rows = [
        _AuditRow(
            id=a.id,
            created_at=a.created_at,
            action=a.action,
            actor=a.actor,
            tool=a.tool,
            tool_version=a.tool_version,
        )
        for a in audits
    ]
    claim_rows = [_ClaimRow(id=c.id, created_at=c.created_at, predicate=c.predicate, text=c.text) for c in claims]
    activity_rows = [
        _ActivityRow(
            id=act.id,
            occurred_at=act.occurred_at,
            created_at=act.created_at,
            entry_type=act.entry_type,
            text=act.text,
        )
        for act in activities
    ]

    case_out = CaseOut.model_validate(case)

    overview_md = "\n".join(
        [
            f"# Overview",
            f"- case_id: {case_out.id}",
            f"- name: {_md_escape_inline(case_out.name or '')}",
            f"- created_at: {case_out.created_at.isoformat()}",
            f"- profile_id: {_md_escape_inline(case_out.profile_id or '')}",
            f"- documents_count: {len(doc_rows)}",
            f"- activities_count: {len(activity_rows)}",
            f"- claims_count: {len(claim_rows)}",
            f"- audit_events_count: {len(audit_rows)}",
        ]
    ).strip() + "\n"

    timeline_lines_with_refs = _build_timeline_items(
        docs=doc_rows,
        audits=audit_rows,
        claims=claim_rows,
        activities=activity_rows,
    )
    timeline_md = "\n".join([row[3] for row in timeline_lines_with_refs]).strip() + ("\n" if timeline_lines_with_refs else "")
    timeline_refs: list[SourceRefOut] = []
    for row in timeline_lines_with_refs:
        timeline_refs.extend(row[4])

    claims_md, claims_refs = _build_claims_grouped(claims=claim_rows)

    evidence_lines: list[str] = ["| document_id | type | sha256 | created_at |", "|---|---|---|---|"]
    evidence_refs: list[SourceRefOut] = []
    for d in doc_rows:
        evidence_lines.append(
            f"| {d.id} | {_md_escape_inline(d.type)} | {_md_escape_inline(d.sha256)} | {d.created_at.isoformat()} |"
        )
        evidence_refs.append(SourceRefOut(source_type="document", source_id=d.id, ts=d.created_at))
    evidence_md = "\n".join(evidence_lines).strip() + "\n"

    fallback_refs: list[SourceRefOut] = []
    if timeline_refs:
        fallback_refs = timeline_refs
    elif evidence_refs:
        fallback_refs = evidence_refs
    elif claims_refs:
        fallback_refs = claims_refs
    elif audit_rows:
        fallback_refs = [SourceRefOut(source_type="audit_event", source_id=audit_rows[0].id, ts=audit_rows[0].created_at)]
    elif activity_rows:
        fallback_refs = [SourceRefOut(source_type="activity", source_id=activity_rows[0].id, ts=activity_rows[0].occurred_at)]

    ppl_loc_veh_sections = _build_people_locations_vehicles_sections(
        claims=claim_rows,
        fallback_refs=fallback_refs,
    )

    timeline_refs_out = timeline_refs or fallback_refs
    claims_refs_out = claims_refs or fallback_refs
    evidence_refs_out = evidence_refs or fallback_refs

    sections: list[ReportSectionOut] = [
        ReportSectionOut(key="overview", title="Overview", content_markdown=overview_md, source_refs=[]),
        *ppl_loc_veh_sections,
        ReportSectionOut(
            key="timeline_summary",
            title="Timeline Summary",
            content_markdown=timeline_md,
            source_refs=timeline_refs_out,
        ),
        ReportSectionOut(
            key="claims_summary",
            title="Claims Summary",
            content_markdown=claims_md,
            source_refs=claims_refs_out,
        ),
        ReportSectionOut(
            key="evidence_index",
            title="Evidence Index",
            content_markdown=evidence_md,
            source_refs=evidence_refs_out,
        ),
    ]

    return ReportDraftOut(case=case_out, generated_at=_utc_now_deterministic(), sections=sections)
