from __future__ import annotations

from fastapi.testclient import TestClient

ZONE_PAYLOAD = {
    "name": "Warehouse",
    "center_latitude": 37.7749,
    "center_longitude": -122.4194,
    "radius_m": 250.0,
    "zone_type": "site",
}


def test_create_zone(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/api/v1/zones/", json=ZONE_PAYLOAD, headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == "Warehouse"
    assert data["center_latitude"] == 37.7749
    assert data["center_longitude"] == -122.4194
    assert data["radius_m"] == 250.0
    assert data["zone_type"] == "site"
    assert data["active"] is True
    assert "id" in data
    assert "created_at" in data


def test_create_zone_validation_errors(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    invalid_payloads = [
        {**ZONE_PAYLOAD, "center_latitude": 91},
        {**ZONE_PAYLOAD, "center_longitude": -181},
        {**ZONE_PAYLOAD, "radius_m": 0},
        {**ZONE_PAYLOAD, "zone_type": "other"},
    ]

    for payload in invalid_payloads:
        resp = client.post("/api/v1/zones/", json=payload, headers=auth_headers)
        assert resp.status_code == 422


def test_list_zones_and_active_filter(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    active_resp = client.post("/api/v1/zones/", json=ZONE_PAYLOAD, headers=auth_headers)
    inactive_resp = client.post(
        "/api/v1/zones/",
        json={**ZONE_PAYLOAD, "name": "Restricted area", "zone_type": "restricted"},
        headers=auth_headers,
    )
    inactive_id = inactive_resp.json()["id"]

    deactivate_resp = client.delete(
        f"/api/v1/zones/{inactive_id}",
        headers=auth_headers,
    )
    assert deactivate_resp.status_code == 200

    all_resp = client.get("/api/v1/zones/", headers=auth_headers)
    active_only_resp = client.get(
        "/api/v1/zones/?active=true",
        headers=auth_headers,
    )
    inactive_only_resp = client.get(
        "/api/v1/zones/?active=false",
        headers=auth_headers,
    )

    assert all_resp.status_code == 200
    assert active_only_resp.status_code == 200
    assert inactive_only_resp.status_code == 200
    all_ids = {zone["id"] for zone in all_resp.json()}
    active_ids = {zone["id"] for zone in active_only_resp.json()}
    inactive_ids = {zone["id"] for zone in inactive_only_resp.json()}
    assert active_resp.json()["id"] in all_ids
    assert active_resp.json()["id"] in active_ids
    assert inactive_id in all_ids
    assert inactive_id not in active_ids
    assert inactive_id in inactive_ids


def test_deactivate_zone(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    create_resp = client.post("/api/v1/zones/", json=ZONE_PAYLOAD, headers=auth_headers)
    zone_id = create_resp.json()["id"]

    resp = client.delete(f"/api/v1/zones/{zone_id}", headers=auth_headers)

    assert resp.status_code == 200
    assert resp.json()["id"] == zone_id
    assert resp.json()["active"] is False


def test_deactivate_unknown_zone(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    resp = client.delete("/api/v1/zones/does-not-exist", headers=auth_headers)

    assert resp.status_code == 404


def test_zones_require_auth(client: TestClient) -> None:
    payload = {**ZONE_PAYLOAD, "name": "Unauthenticated"}

    create_resp = client.post("/api/v1/zones/", json=payload)
    list_resp = client.get("/api/v1/zones/")
    delete_resp = client.delete("/api/v1/zones/does-not-exist")

    assert create_resp.status_code == 403
    assert list_resp.status_code == 403
    assert delete_resp.status_code == 403
