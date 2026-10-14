from __future__ import annotations

from fastapi.testclient import TestClient


def _create(client: TestClient, auth_headers: dict[str, str], **overrides: object) -> dict:
    body = {
        "name": "Depot North",
        "center_latitude": 37.7749,
        "center_longitude": -122.4194,
        "radius_m": 500.0,
        "kind": "inclusion",
    }
    body.update(overrides)
    resp = client.post("/api/v1/geofences/", json=body, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_create_geofence_returns_persisted_row(client, auth_headers):
    created = _create(client, auth_headers, name="Depot Alpha")
    assert created["name"] == "Depot Alpha"
    assert created["kind"] == "inclusion"
    assert created["id"].startswith("gf-")


def test_list_geofences_includes_created(client, auth_headers):
    created = _create(client, auth_headers, name="Depot Beta")
    resp = client.get("/api/v1/geofences/", headers=auth_headers)
    assert resp.status_code == 200
    assert created["id"] in [g["id"] for g in resp.json()]


def test_events_for_unknown_geofence_is_404(client, auth_headers):
    resp = client.get("/api/v1/geofences/gf-missing/events", headers=auth_headers)
    assert resp.status_code == 404


def test_delete_geofence_removes_it(client, auth_headers):
    created = _create(client, auth_headers, name="Depot Gamma")
    assert (
        client.delete(f"/api/v1/geofences/{created['id']}", headers=auth_headers).status_code
        == 200
    )
    resp = client.get("/api/v1/geofences/", headers=auth_headers)
    assert created["id"] not in [g["id"] for g in resp.json()]


def test_vehicles_status_filter(client, auth_headers):
    resp = client.get("/api/v1/vehicles/?status=maintenance", headers=auth_headers)
    assert resp.status_code == 200
    assert all(v["status"] == "maintenance" for v in resp.json())


def test_fleet_summary_totals(client, auth_headers):
    resp = client.get("/api/v1/vehicles/summary", headers=auth_headers)
    assert resp.status_code == 200
    payload = resp.json()
    assert payload["total"] == sum(payload["by_status"].values())
