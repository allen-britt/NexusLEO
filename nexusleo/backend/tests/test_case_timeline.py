"""Case timeline read API tests (PR #6)."""
from __future__ import annotations


def _stable_id(item: dict) -> str:
    t = item["item_type"]
    if t == "DOCUMENT_ADDED":
        return item["document"]["document_id"]
    if t == "AUDIT_EVENT":
        return item["audit"]["audit_event_id"]
    if t == "CLAIM_CREATED":
        return item["claim"]["claim_id"]
    if t == "ACTIVITY_ATTACHED":
        return item["activity"]["activity_id"]
    if t == "ARTIFACT_ADDED":
        return item["artifact"]["artifact_id"]
    raise AssertionError(f"unknown item_type {t}")


def test_case_timeline_unified_and_deterministic(client) -> None:
    case_resp = client.post("/cases", json={"name": "Timeline Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    user_resp = client.post("/users", json={"display_name": "Officer Timeline", "badge_id": "6666"})
    user_resp.raise_for_status()
    user_id = user_resp.json()["id"]

    start_resp = client.post("/shifts/start", json={"user_id": user_id, "device_id": "unit-6"})
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
        json={"entry_type": "FIELD_NOTE", "text": note_text, "actor": "Officer Timeline"},
    )
    log_note.raise_for_status()
    activity_id = log_note.json()["activity_log_entry"]["id"]

    attach = client.post(
        f"/cases/{case_id}/attach_activity",
        json={"activity_log_entry_id": activity_id, "mode": "COPY_NOTE_AND_INGEST", "actor": "Officer Timeline"},
    )
    attach.raise_for_status()

    timeline = client.get(f"/cases/{case_id}/timeline")
    timeline.raise_for_status()
    items = timeline.json()

    assert isinstance(items, list)

    types = [it["item_type"] for it in items]
    assert "DOCUMENT_ADDED" in types
    assert "AUDIT_EVENT" in types
    assert "CLAIM_CREATED" in types
    assert "ACTIVITY_ATTACHED" in types

    # Deterministic ordering: (ts asc, item_type asc, stable_id asc)
    prev = None
    for it in items:
        key = (it["ts"], it["item_type"], _stable_id(it))
        if prev is not None:
            assert key >= prev
        prev = key

    page1 = client.get(f"/cases/{case_id}/timeline?limit=2&offset=0")
    page1.raise_for_status()
    p1 = page1.json()

    page2 = client.get(f"/cases/{case_id}/timeline?limit=2&offset=2")
    page2.raise_for_status()
    p2 = page2.json()

    ids1 = {(it["item_type"], _stable_id(it)) for it in p1}
    ids2 = {(it["item_type"], _stable_id(it)) for it in p2}
    assert ids1.isdisjoint(ids2)

    combined = p1 + p2
    assert combined == items[0:4]
