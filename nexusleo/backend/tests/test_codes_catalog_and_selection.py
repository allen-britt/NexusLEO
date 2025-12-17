from __future__ import annotations

from uuid import UUID


def test_codes_search_and_selection_idempotent(client) -> None:
    case_resp = client.post("/cases", json={"name": "Codes Case"})
    case_resp.raise_for_status()
    case_id = case_resp.json()["id"]

    search1 = client.get("/codes/search", params={"jurisdiction": "MD"})
    search1.raise_for_status()
    data1 = search1.json()

    search2 = client.get("/codes/search", params={"jurisdiction": "MD"})
    search2.raise_for_status()
    data2 = search2.json()

    assert data1 == data2
    assert data1["total"] >= 2
    assert data1["items"]

    first_code = data1["items"][0]
    catalog_id = first_code["id"]

    sel_payload = {"catalog_type": "CODE", "catalog_id": catalog_id, "actor": "Officer Codes"}
    sel_resp1 = client.post(f"/cases/{case_id}/codes/select", json=sel_payload)
    sel_resp1.raise_for_status()
    out1 = sel_resp1.json()
    assert out1["created"] is True
    assert out1["selection"]["catalog_id"] == catalog_id

    sel_resp2 = client.post(f"/cases/{case_id}/codes/select", json=sel_payload)
    sel_resp2.raise_for_status()
    out2 = sel_resp2.json()
    assert out2["created"] is False
    assert out2["selection"]["selection_id"] == out1["selection"]["selection_id"]

    timeline = client.get(f"/cases/{case_id}/timeline")
    timeline.raise_for_status()
    items = timeline.json()
    types = [it["item_type"] for it in items]
    assert "CODE_SELECTED" in types
    assert "AUDIT_EVENT" in types

    audit_actions = [it["audit"]["action"] for it in items if it["item_type"] == "AUDIT_EVENT"]
    assert audit_actions.count("code_selected") == 1
    sel_items = [it for it in items if it["item_type"] == "CODE_SELECTED"]
    assert len(sel_items) == 1
    selection = sel_items[0]["code_selection"]
    assert selection["catalog_type"] == "CODE"
    assert UUID(selection["selection_id"]) == UUID(out1["selection"]["selection_id"])
