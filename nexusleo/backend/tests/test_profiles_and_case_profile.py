from __future__ import annotations

from app.models import AuditEvent


def test_profiles_list_and_case_profile_and_guidance_filtering(client, db_session_factory) -> None:
    # List profiles should be deterministic and contain 3 entries.
    p1 = client.get("/profiles")
    p1.raise_for_status()
    profiles1 = p1.json()

    p2 = client.get("/profiles")
    p2.raise_for_status()
    assert profiles1 == p2.json()

    assert len(profiles1) == 3
    assert [p["jurisdiction"] for p in profiles1] == ["DC", "MD", "VA"]

    md = next(p for p in profiles1 if p["profile_id"] == "dmv-md")

    # Create a case.
    case_resp = client.post("/cases", json={"name": "Profiled Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    # Attach profile to case.
    set_resp = client.post(f"/cases/{case_id}/profile", json={"profile_id": "dmv-md", "actor": "tester"})
    set_resp.raise_for_status()
    assert set_resp.json()["profile_id"] == "dmv-md"

    # Add doc + ingest.
    doc_resp = client.post(
        f"/cases/{case_id}/documents",
        json={
            "type": "TRANSCRIPT",
            "text": "ALPHA: I met with John Smith in Baltimore.",
            "metadata": {"source": "test"},
        },
    )
    doc_resp.raise_for_status()
    document_id = doc_resp.json()["id"]

    ingest_resp = client.post(f"/cases/{case_id}/ingest", json={"document_id": document_id, "actor": "tester"})
    ingest_resp.raise_for_status()

    g1 = client.get(f"/cases/{case_id}/guidance")
    g1.raise_for_status()
    body1 = g1.json()

    g2 = client.get(f"/cases/{case_id}/guidance")
    g2.raise_for_status()
    assert body1 == g2.json()

    assert body1["profile_id"] == "dmv-md"
    allowed = set(md["guidance_categories"])
    for item in body1["items"]:
        assert item["category"] in allowed

    # Verify audit event.
    session = db_session_factory()
    evt = (
        session.query(AuditEvent)
        .filter(AuditEvent.case_id == case_id)
        .filter(AuditEvent.action == "case_profile_set")
        .order_by(AuditEvent.created_at.desc(), AuditEvent.id.desc())
        .first()
    )
    assert evt is not None
    assert evt.tool == "nexusleo.profile"
    assert evt.tool_version == "0.1.0"
    assert evt.actor == "tester"
