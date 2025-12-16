"""Attach activity log entries to cases (PR #5)."""
from __future__ import annotations

import hashlib

from app.models import ActivityLogEntry, SourceDocument


def test_attach_activity_to_case_link_and_copy_ingest(client, db_session_factory) -> None:
    user_resp = client.post("/users", json={"display_name": "Officer Three", "badge_id": "3333"})
    user_resp.raise_for_status()
    user_id = user_resp.json()["id"]

    start_resp = client.post("/shifts/start", json={"user_id": user_id, "device_id": "unit-3"})
    start_resp.raise_for_status()
    shift_id = start_resp.json()["shift_id"]

    note_text = "\n".join(
        [
            "ALPHA: I met with John Smith in Baltimore on 2025-01-02.",
            "BRAVO: I met with John Smith in Baltimore.",
        ]
    )

    log_note = client.post(
        f"/shifts/{shift_id}/log_note",
        json={"entry_type": "FIELD_NOTE", "text": note_text, "actor": "Officer Three"},
    )
    log_note.raise_for_status()
    body = log_note.json()

    activity_id = body["activity_log_entry"]["id"]

    case_resp = client.post("/cases", json={"name": "Case X"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    attach1 = client.post(
        f"/cases/{case_id}/attach_activity",
        json={"activity_log_entry_id": activity_id, "mode": "LINK_ONLY", "actor": "Officer Three"},
    )
    attach1.raise_for_status()
    attach1_body = attach1.json()

    assert attach1_body["linked"] is True
    assert attach1_body["claims"] == []

    session = db_session_factory()
    entry = session.get(ActivityLogEntry, activity_id)
    assert entry is not None
    assert str(entry.case_id) == case_id

    attach2 = client.post(
        f"/cases/{case_id}/attach_activity",
        json={"activity_log_entry_id": activity_id, "mode": "COPY_NOTE_AND_INGEST", "actor": "Officer Three"},
    )
    attach2.raise_for_status()
    attach2_body = attach2.json()

    assert attach2_body["note_document_id"] is not None
    assert attach2_body["ingest_result"] is not None
    assert len(attach2_body["claims"]) >= 1
    assert attach2_body["claims"][0]["confidence"] is not None
    assert len(attach2_body["claims"][0]["evidence"]) >= 1

    note_document_id = attach2_body["note_document_id"]

    # Re-attach with copy+ingest should reuse NOTE document idempotently by (case_id, sha256)
    attach3 = client.post(
        f"/cases/{case_id}/attach_activity",
        json={"activity_log_entry_id": activity_id, "mode": "COPY_NOTE_AND_INGEST", "actor": "Officer Three"},
    )
    attach3.raise_for_status()
    attach3_body = attach3.json()

    assert attach3_body["note_document_id"] == note_document_id

    sha256 = hashlib.sha256(note_text.encode("utf-8")).hexdigest()
    docs = session.query(SourceDocument).filter(SourceDocument.case_id == case_id, SourceDocument.sha256 == sha256).all()
    assert len(docs) == 1
