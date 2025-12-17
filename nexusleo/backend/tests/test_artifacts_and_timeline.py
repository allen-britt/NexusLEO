from __future__ import annotations

from app.models import AuditEvent


def test_artifacts_list_timeline_and_audit(client, db_session_factory) -> None:
    case_resp = client.post("/cases", json={"name": "Artifacts Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    create = client.post(
        f"/cases/{case_id}/artifacts",
        json={
            "kind": "video",
            "label": "Body Cam Clip",
            "uri": "file:///evidence/clip1.mp4",
            "sha256": "a" * 64,
            "actor": "tester",
            "metadata": {"source": "unit"},
        },
    )
    create.raise_for_status()
    artifact_id = create.json()["id"]

    l1 = client.get(f"/cases/{case_id}/artifacts")
    l1.raise_for_status()
    body1 = l1.json()

    l2 = client.get(f"/cases/{case_id}/artifacts")
    l2.raise_for_status()
    assert body1 == l2.json()

    assert len(body1) == 1
    assert body1[0]["id"] == artifact_id

    timeline = client.get(f"/cases/{case_id}/timeline")
    timeline.raise_for_status()
    items = timeline.json()

    assert any(it["item_type"] == "ARTIFACT_ADDED" for it in items)

    art_item = next(it for it in items if it["item_type"] == "ARTIFACT_ADDED")
    assert art_item["artifact"]["artifact_id"] == artifact_id
    assert art_item["artifact"]["kind"] == "video"
    assert art_item["artifact"]["label"] == "Body Cam Clip"

    session = db_session_factory()
    evt = (
        session.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .filter(AuditEvent.action == "artifact_added")
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .first()
    )
    assert evt is not None
    assert evt.tool == "nexusleo.ingest"
    assert evt.tool_version == "0.1.0"
    assert evt.actor == "tester"
    assert evt.output_refs_json.get("artifact_id") == artifact_id
