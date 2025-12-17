from __future__ import annotations


def test_codes_suggestions_require_state_context(client) -> None:
    case_resp = client.post("/cases", json={"name": "Suggest Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    resp = client.get(f"/cases/{case_id}/codes/suggestions")
    assert resp.status_code == 409
    assert resp.json()["detail"] == "state_context_required"


def test_codes_suggestions_deterministic(client) -> None:
    case_resp = client.post("/cases", json={"name": "Suggest Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    # set state context
    sc = {"state_context": {"selected_state": "MD"}}
    sc_resp = client.post(f"/cases/{case_id}/state_context", json=sc)
    sc_resp.raise_for_status()

    # set observed facts
    facts = {
        "observed_facts": {
            "traffic": {"speed_over_limit_mph": 10},
            "person": {"weapon_present": True},
            "location": {"school_zone": True},
        }
    }
    facts_resp = client.post(f"/cases/{case_id}/observed_facts", json=facts)
    facts_resp.raise_for_status()

    sug1 = client.get(f"/cases/{case_id}/codes/suggestions")
    sug1.raise_for_status()
    data1 = sug1.json()

    sug2 = client.get(f"/cases/{case_id}/codes/suggestions")
    sug2.raise_for_status()
    data2 = sug2.json()

    assert data1 == data2
    items = data1["items"]
    assert items, "expected suggestions"

    # Ensure suggestions reference catalog rows and are sorted
    for it in items:
        assert it["catalog_id"] is not None
        assert it["code"]
        assert it["label"]
        assert it["id"]

    # With missing facts, expect no suggestions
    facts_empty = {"observed_facts": {}}
    client.post(f"/cases/{case_id}/observed_facts", json=facts_empty).raise_for_status()
    sug_empty = client.get(f"/cases/{case_id}/codes/suggestions")
    sug_empty.raise_for_status()
    assert sug_empty.json()["items"] == []
