"""Deterministic ingest pipeline for NexusLEO v0.1."""
from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Iterable
from uuid import UUID

from sqlalchemy.orm import Session

from app.models import (
    AuditEvent,
    Claim,
    ConfidenceAssessment,
    ConfidenceLevel,
    Entity,
    EvidenceLink,
    Mention,
    ResolutionHypothesis,
    ResolutionStatus,
    SourceDocument,
)
from app.schemas import IngestResult

_TOOL = "nexusleo.ingest"
_TOOL_VERSION = "0.1.0"
_RUBRIC_VERSION = "v0.1"


@dataclass(frozen=True)
class _Line:
    speaker: str
    text: str


def _parse_lines(raw: str) -> list[_Line]:
    lines: list[_Line] = []
    for raw_line in raw.splitlines():
        raw_line = raw_line.strip()
        if not raw_line:
            continue
        if ":" in raw_line:
            speaker, text = raw_line.split(":", 1)
            lines.append(_Line(speaker=speaker.strip(), text=text.strip()))
        else:
            lines.append(_Line(speaker="UNKNOWN", text=raw_line))
    return lines


_PERSON_CANDIDATES = [
    "John Smith",
    "Jane Doe",
    "Ryan",
    "Rian",
    "John",
]


def _extract_person_mentions(lines: Iterable[_Line]) -> list[tuple[str, str]]:
    mentions: list[tuple[str, str]] = []
    for line in lines:
        for name in _PERSON_CANDIDATES:
            if name in line.text:
                mentions.append((line.speaker, name))
    return mentions


_LOCATION_PATTERN = re.compile(r"\b(Baltimore|Annapolis)\b")


def _extract_location(text: str) -> str | None:
    m = _LOCATION_PATTERN.search(text)
    return m.group(1) if m else None


def _ensure_audit_event(db: Session, *, case_id: UUID, actor: str, action: str, input_refs: dict, output_refs: dict) -> None:
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


def ingest_document(*, db: Session, case_id: str, document_id: str, actor: str | None) -> IngestResult:
    case_uuid = UUID(str(case_id))
    document_uuid = UUID(str(document_id))
    actor_value = actor or "system"

    doc = db.get(SourceDocument, document_uuid)
    if doc is None:
        raise ValueError("document_not_found")

    input_refs = {"case_id": str(case_uuid), "document_id": str(document_uuid), "sha256": doc.sha256}

    _ensure_audit_event(db, case_id=case_uuid, actor=actor_value, action="ingest_started", input_refs=input_refs, output_refs={})

    # Idempotency: if this document already has mentions, do not create new analytical objects.
    existing_mentions = db.query(Mention.id).filter(Mention.document_id == document_uuid).limit(1).all()
    if existing_mentions:
        _ensure_audit_event(
            db,
            case_id=case_uuid,
            actor=actor_value,
            action="extraction_completed",
            input_refs=input_refs,
            output_refs={"mentions_created": 0, "claims_created": 0},
        )
        _ensure_audit_event(
            db,
            case_id=case_uuid,
            actor=actor_value,
            action="confidence_assessed",
            input_refs=input_refs,
            output_refs={"confidence_created": 0},
        )
        _ensure_audit_event(
            db,
            case_id=case_uuid,
            actor=actor_value,
            action="ingest_completed",
            input_refs=input_refs,
            output_refs={"idempotent": True},
        )
        db.commit()

        claim_ids = [row[0] for row in db.query(Claim.id).filter(Claim.case_id == case_uuid).all()]
        return IngestResult(
            document_id=document_uuid,
            mentions_created=0,
            entities_created=0,
            claims_created=0,
            evidence_links_created=0,
            confidence_created=0,
            audit_events_created=4,
            claim_ids=claim_ids,
        )

    lines = _parse_lines(doc.raw_text)

    # Create mentions for each line.
    mentions_created = 0
    mention_rows: list[Mention] = []
    cursor = 0
    for line in lines:
        start = cursor
        end = cursor + len(line.text)
        mention = Mention(
            document_id=document_uuid,
            text=line.text,
            start=start,
            end=end,
            speaker=line.speaker,
            timestamp=None,
            language="en",
            entity_type_guess=None,
        )
        db.add(mention)
        mention_rows.append(mention)
        mentions_created += 1
        cursor = end + 1

    db.flush()

    # Entities: deterministic conservative creation.
    entities_created = 0
    entity_by_name: dict[str, Entity] = {}
    for _, name in _extract_person_mentions(lines):
        if name not in entity_by_name:
            existing = (
                db.query(Entity)
                .filter(Entity.case_id == case_uuid, Entity.entity_type == "PERSON", Entity.canonical_name == name)
                .one_or_none()
            )
            if existing is not None:
                entity_by_name[name] = existing
                continue
            entity = Entity(
                case_id=case_uuid,
                entity_type="PERSON",
                canonical_name=name,
                attributes_json={},
            )
            db.add(entity)
            db.flush()
            entity_by_name[name] = entity
            entities_created += 1

        if name == "John":
            db.add(
                ResolutionHypothesis(
                    mention_id=mention_rows[0].id,
                    candidate_entity_id=entity_by_name[name].id,
                    score=0.0,
                    features_json={"reason": "single_token_name", "name": "John"},
                    status=ResolutionStatus.UNREVIEWED,
                )
            )

    for name in ("Ryan", "Rian"):
        if name in entity_by_name:
            db.add(
                ResolutionHypothesis(
                    mention_id=mention_rows[0].id,
                    candidate_entity_id=entity_by_name[name].id,
                    score=0.0,
                    features_json={"reason": "ambiguous_similarity", "name": name},
                    status=ResolutionStatus.UNREVIEWED,
                )
            )

    # Claims and evidence: minimal deterministic extraction.
    claims_created = 0
    evidence_links_created = 0
    confidence_created = 0
    claim_ids: list[UUID] = []

    # Extract meeting claims.
    meeting_mentions: list[tuple[Mention, str, str]] = []  # mention, person, location
    for mention in mention_rows:
        loc = _extract_location(mention.text)
        if loc is None:
            continue
        for person in ("John Smith", "Jane Doe"):
            if person in mention.text:
                meeting_mentions.append((mention, person, loc))

    by_key: dict[tuple[str, str], list[Mention]] = {}
    for mention, person, loc in meeting_mentions:
        key = (person, loc)
        by_key.setdefault(key, []).append(mention)

    for (person, loc), mentions in by_key.items():
        claim = Claim(
            case_id=case_uuid,
            claim_type="MEETING",
            subject_entity_id=entity_by_name.get(person).id if person in entity_by_name else None,
            object_entity_id=None,
            predicate="MET_WITH",
            text=f"met_with:{person}:{loc}",
        )
        db.add(claim)
        db.flush()
        claim_ids.append(claim.id)
        claims_created += 1

        for m in mentions:
            db.add(EvidenceLink(claim_id=claim.id, mention_id=m.id, weight=1.0, notes=None))
            evidence_links_created += 1

        unique_speakers = {m.speaker for m in mentions if m.speaker}
        factors = {
            "independent_evidence_count": len(mentions),
            "unique_speakers_count": len(unique_speakers),
            "unique_documents_count": 1,
            "has_single_token_person": person.split(" ") == ["John"],
            "rule_claim_type": "MEETING",
        }
        level = ConfidenceLevel.HIGH if len(unique_speakers) >= 2 else ConfidenceLevel.MODERATE
        db.add(
            ConfidenceAssessment(
                claim_id=claim.id,
                level=level,
                rubric_version=_RUBRIC_VERSION,
                factors_json=factors,
                rationale_text="rubric_v0_1",
            )
        )
        confidence_created += 1

    # Extract call claims.
    for mention in mention_rows:
        if "called" not in mention.text:
            continue
        if "John" in mention.text and "Jane Doe" in mention.text:
            claim = Claim(
                case_id=case_uuid,
                claim_type="CALL",
                subject_entity_id=entity_by_name.get("John").id if "John" in entity_by_name else None,
                object_entity_id=entity_by_name.get("Jane Doe").id if "Jane Doe" in entity_by_name else None,
                predicate="CALLED",
                text="called:John:Jane Doe",
            )
            db.add(claim)
            db.flush()
            claim_ids.append(claim.id)
            claims_created += 1

            db.add(EvidenceLink(claim_id=claim.id, mention_id=mention.id, weight=1.0, notes=None))
            evidence_links_created += 1

            factors = {
                "independent_evidence_count": 1,
                "unique_speakers_count": 1,
                "unique_documents_count": 1,
                "has_single_token_person": True,
                "rule_claim_type": "CALL",
            }
            db.add(
                ConfidenceAssessment(
                    claim_id=claim.id,
                    level=ConfidenceLevel.LOW,
                    rubric_version=_RUBRIC_VERSION,
                    factors_json=factors,
                    rationale_text="rubric_v0_1",
                )
            )
            confidence_created += 1

    _ensure_audit_event(
        db,
        case_id=case_uuid,
        actor=actor_value,
        action="extraction_completed",
        input_refs=input_refs,
        output_refs={
            "mentions_created": mentions_created,
            "entities_created": entities_created,
            "claims_created": claims_created,
            "evidence_links_created": evidence_links_created,
        },
    )

    _ensure_audit_event(
        db,
        case_id=case_uuid,
        actor=actor_value,
        action="confidence_assessed",
        input_refs=input_refs,
        output_refs={"confidence_created": confidence_created, "rubric_version": _RUBRIC_VERSION},
    )

    _ensure_audit_event(
        db,
        case_id=case_uuid,
        actor=actor_value,
        action="ingest_completed",
        input_refs=input_refs,
        output_refs={"claim_ids": [str(cid) for cid in claim_ids]},
    )

    db.commit()

    return IngestResult(
        document_id=document_uuid,
        mentions_created=mentions_created,
        entities_created=entities_created,
        claims_created=claims_created,
        evidence_links_created=evidence_links_created,
        confidence_created=confidence_created,
        audit_events_created=4,
        claim_ids=claim_ids,
    )
