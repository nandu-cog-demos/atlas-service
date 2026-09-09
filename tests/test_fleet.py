from __future__ import annotations

from fastapi.testclient import TestClient


def _telemetry(vehicle_id: str, fuel: float = 50.0, speed: float = 40.0) -> dict:
    return {
        "vehicle_id": vehicle_id,
        "latitude": 37.0,
        "longitude": -122.0,
        "speed_kmh": speed,
        "heading": 90.0,
        "fuel_level": fuel,
        "timestamp": "2024-01-15T12:00:00Z",
    }


def test_list_vehicles_filter_by_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/", params={"status": "maintenance"}, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data
    assert all(v["status"] == "maintenance" for v in data)


def test_list_vehicles_invalid_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/", params={"status": "flying"}, headers=auth_headers)
    assert resp.status_code == 422


def test_update_vehicle_status(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch(
        "/api/v1/vehicles/v-002/status", json={"status": "offline"}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["status"] == "offline"

    resp = client.get("/api/v1/vehicles/v-002", headers=auth_headers)
    assert resp.json()["status"] == "offline"

    client.patch("/api/v1/vehicles/v-002/status", json={"status": "idle"}, headers=auth_headers)


def test_update_vehicle_status_invalid(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch(
        "/api/v1/vehicles/v-002/status", json={"status": "flying"}, headers=auth_headers
    )
    assert resp.status_code == 422


def test_update_vehicle_status_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch(
        "/api/v1/vehicles/v-999/status", json={"status": "idle"}, headers=auth_headers
    )
    assert resp.status_code == 404


def test_fleet_summary(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = _telemetry("v-001", fuel=80, speed=60)
    client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)

    resp = client.get("/api/v1/vehicles/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_vehicles"] == sum(data["by_status"].values())
    assert set(data["by_status"]) == {"active", "idle", "maintenance", "offline"}
    assert data["average_fuel_level"] is not None
    assert data["stale_threshold_minutes"] == 30
    # v-002 (idle, last seen in 2024) is stale; v-003 is in maintenance and excluded
    assert data["stale_vehicles"] >= 1


def test_fleet_summary_custom_threshold(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get(
        "/api/v1/vehicles/summary", params={"stale_after_minutes": 5}, headers=auth_headers
    )
    assert resp.status_code == 200
    assert resp.json()["stale_threshold_minutes"] == 5

    resp = client.get(
        "/api/v1/vehicles/summary", params={"stale_after_minutes": 0}, headers=auth_headers
    )
    assert resp.status_code == 422


def test_batch_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    body = {"records": [_telemetry("v-001"), _telemetry("v-002"), _telemetry("v-999")]}
    resp = client.post("/api/v1/telemetry/batch", json=body, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["accepted"] == 2
    assert data["rejected"] == 1
    assert data["rejected_vehicle_ids"] == ["v-999"]


def test_batch_telemetry_empty(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.post("/api/v1/telemetry/batch", json={"records": []}, headers=auth_headers)
    assert resp.status_code == 422


def test_batch_telemetry_invalid_record(client: TestClient, auth_headers: dict[str, str]) -> None:
    bad = _telemetry("v-001")
    bad["fuel_level"] = 150
    resp = client.post("/api/v1/telemetry/batch", json={"records": [bad]}, headers=auth_headers)
    assert resp.status_code == 422
