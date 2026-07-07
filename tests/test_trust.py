from __future__ import annotations

from fastapi.testclient import TestClient


def test_trust_center_is_public(client: TestClient) -> None:
    resp = client.get("/api/v1/trust/")
    assert resp.status_code == 200


def test_trust_center_shape(client: TestClient) -> None:
    body = client.get("/api/v1/trust/").json()

    assert body["overview"]
    assert body["certifications"]
    assert {"name", "status", "description"} <= set(body["certifications"][0])
    assert body["security_practices"][0]["items"]
    assert {"name", "purpose", "location"} <= set(body["subprocessors"][0])
    assert body["service_status"]["state"] == "operational"
    assert 0 <= body["service_status"]["uptime_90d"] <= 100
    assert body["resources"]
