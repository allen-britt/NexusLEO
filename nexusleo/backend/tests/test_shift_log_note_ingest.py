"""Shift log_note -> NOTE document -> ingest workflow tests (PR #4)."""
from __future__ import annotations


def test_shift_log_note_auto_ingest_and_idempotent_document(client) -> None:
    user_resp = client.post("/users", json={"display_name": "Officer Two", "badge_id": "2222"})
    user_resp.raise_for_status()
    user_id = user_resp.json()["id"]

    start_resp = client.post("/shifts/start", json={"user_id": user_id, "device_id": "unit-2"})
    start_resp.raise_for_status()
    shift_id = start_resp.json()["shift_id"]

    note_text = "\n".join(
        [
            "ALPHA: I met with John Smith in Baltimore on 2025-01-02.",
            "BRAVO: I met with John Smith in Baltimore.",
        ]
    )

    resp1 = client.post(
        f"/shifts/{shift_id}/log_note",
        json={"entry_type": "FIELD_NOTE", "text": note_text, "actor": "Officer Two"},
    )
    resp1.raise_for_status()
    body1 = resp1.json()

    assert body1["activity_log_entry"]["id"]
    assert body1["document"]["id"]
    assert body1["document"]["type"] == "NOTE"
    assert body1["ingest_result"]["claims_created"] >= 1
    assert len(body1["claims"]) >= 1
    assert body1["claims"][0]["confidence"] is not None
    assert len(body1["claims"][0]["evidence"]) >= 1

    activity_id_1 = body1["activity_log_entry"]["id"]
    document_id_1 = body1["document"]["id"]

    timeline = client.get(f"/shifts/{shift_id}/timeline")
    timeline.raise_for_status()
    items = timeline.json()

    assert any(
        it.get("id") == activity_id_1 and it.get("source_document_id") == document_id_1 and it.get("timeline_item_type") == "NOTE_CREATED"
        for it in items
    )

    resp2 = client.post(
        f"/shifts/{shift_id}/log_note",
        json={"entry_type": "FIELD_NOTE", "text": note_text, "actor": "Officer Two"},
    )
    resp2.raise_for_status()
    body2 = resp2.json()

    assert body2["document"]["id"] == document_id_1
