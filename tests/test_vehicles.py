from __future__ import annotations

from fastapi.testclient import TestClient


def test_list_vehicles(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert isinstance(data, list)
    assert len(data) >= 3
    names = {v["name"] for v in data}
    assert "Truck Alpha" in names


def test_get_vehicle_detail(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/v-001", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["id"] == "v-001"
    assert data["name"] == "Truck Alpha"
    assert data["status"] == "active"


def test_get_vehicle_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/v-999", headers=auth_headers)
    assert resp.status_code == 404


def test_get_vehicle_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)


def test_get_latest_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    older = {
        "vehicle_id": "v-001",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 40.0,
        "heading": 90.0,
        "fuel_level": 80.0,
        "timestamp": "2024-01-15T11:00:00Z",
    }
    newer = {**older, "speed_kmh": 65.0, "timestamp": "2024-01-15T12:30:00Z"}
    for payload in (older, newer):
        resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    resp = client.get("/api/v1/vehicles/v-001/telemetry/latest", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["vehicle_id"] == "v-001"
    assert data["speed_kmh"] == 65.0
    assert data["timestamp"] == "2024-01-15T12:30:00Z"
    for field in (
        "id", "latitude", "longitude", "heading", "fuel_level", "received_at",
    ):
        assert field in data


def test_get_latest_telemetry_vehicle_not_found(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-999/telemetry/latest", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Vehicle not found"


def test_get_latest_telemetry_no_records(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-003/telemetry/latest", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "No telemetry for vehicle"


def test_get_latest_telemetry_no_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry/latest")
    assert resp.status_code == 403
