"""Audit event sequence stress tests."""
from __future__ import annotations

from tests.utils import load_fixture
from app.models import AuditEvent


def _create_case(client) -> str:
    response = client.post("/cases", json={})
    response.raise_for_status()
    return response.json()["id"]


def _create_document(client, case_id: str, text: str) -> str:
    response = client.post(
        f"/cases/{case_id}/documents",
        json={"type": "TRANSCRIPT", "text": text, "metadata": {}},
    )
    response.raise_for_status()
    return response.json()["id"]


def _ingest(client, case_id: str, document_id: str) -> None:
    response = client.post(f"/cases/{case_id}/ingest", json={"document_id": document_id})
    response.raise_for_status()


def test_audit_event_sequence(client, db_session_factory) -> None:
    text = load_fixture("corroboration_two_speakers.txt")
    case_id = _create_case(client)
    document_id = _create_document(client, case_id, text)
    _ingest(client, case_id, document_id)

    session = db_session_factory()
    events = (
        session.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .order_by(AuditEvent.created_at.asc())
        .all()
    )
    assert len(events) >= 4, "Expected at least four ingest audit events"

    tail = events[-4:]
    expected_actions = [
        "ingest_started",
        "extraction_completed",
        "confidence_assessed",
        "ingest_completed",
    ]
    actual_actions = [event.action for event in tail]
    assert actual_actions == expected_actions, f"Unexpected audit sequence: {actual_actions}"

    for event in tail:
        assert event.tool == "nexusleo.ingest"
        assert event.tool_version == "0.1.0"
        assert event.actor, "Actor must be recorded on audit events"
