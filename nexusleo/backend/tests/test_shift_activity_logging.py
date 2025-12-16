"""Shift + activity logging workflow tests (PR #3)."""
from __future__ import annotations

from datetime import datetime, timezone

from app.models import AuditEvent


def test_shift_activity_logging_workflow(client, db_session_factory) -> None:
    # Create a user
    user_resp = client.post("/users", json={"display_name": "Officer One", "badge_id": "1234"})
    user_resp.raise_for_status()
    user_id = user_resp.json()["id"]

    # Start a shift
    start_resp = client.post("/shifts/start", json={"user_id": user_id, "device_id": "unit-1"})
    start_resp.raise_for_status()
    shift_id = start_resp.json()["shift_id"]

    # Log two entries out of chronological order to validate deterministic sorting.
    t1 = datetime(2025, 1, 1, 10, 0, 0, tzinfo=timezone.utc).isoformat()
    t0 = datetime(2025, 1, 1, 9, 0, 0, tzinfo=timezone.utc).isoformat()

    log1 = client.post(
        f"/shifts/{shift_id}/log",
        json={"entry_type": "TRAFFIC_STOP", "text": "Stop on I-95", "occurred_at": t1, "metadata": {}},
    )
    log1.raise_for_status()

    log0 = client.post(
        f"/shifts/{shift_id}/log",
        json={"entry_type": "START_SHIFT", "text": "Roll call", "occurred_at": t0, "metadata": {}},
    )
    log0.raise_for_status()

    # Timeline should be ordered by occurred_at, then created_at, then id.
    timeline = client.get(f"/shifts/{shift_id}/timeline")
    timeline.raise_for_status()
    items = timeline.json()

    assert len(items) == 2
    assert items[0]["occurred_at"].startswith("2025-01-01T09:00:00")
    assert items[1]["occurred_at"].startswith("2025-01-01T10:00:00")

    # End shift
    end_resp = client.post(f"/shifts/{shift_id}/end")
    end_resp.raise_for_status()
    assert end_resp.json()["shift_id"] == shift_id

    # Verify audit events were created and are queryable deterministically.
    session = db_session_factory()
    events = (
        session.query(AuditEvent)
        .filter(AuditEvent.input_refs_json["shift_id"].astext == shift_id)
        .order_by(AuditEvent.created_at.asc(), AuditEvent.id.asc())
        .all()
    )

    actions = [e.action for e in events]
    assert actions.count("shift_started") == 1
    assert actions.count("activity_logged") == 2
    assert actions.count("shift_ended") == 1

    for e in events:
        assert e.tool == "nexusleo.shift"
        assert e.tool_version == "0.1.0"
        assert e.actor
