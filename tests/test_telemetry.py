from __future__ import annotations

from fastapi.testclient import TestClient


def test_ingest_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "vehicle_id": "v-001",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 55.0,
        "heading": 180.0,
        "fuel_level": 72.5,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["vehicle_id"] == "v-001"
    assert "id" in data
    assert "received_at" in data


def test_ingest_telemetry_invalid_coords(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "vehicle_id": "v-001",
        "latitude": 999.0,
        "longitude": -122.4194,
        "speed_kmh": 55.0,
        "heading": 180.0,
        "fuel_level": 72.5,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
    assert resp.status_code == 422


def test_ingest_telemetry_unknown_vehicle(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "vehicle_id": "v-does-not-exist",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 55.0,
        "heading": 180.0,
        "fuel_level": 72.5,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
    assert resp.status_code == 404


def test_ingest_telemetry_preserves_maintenance_status(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-003", headers=auth_headers)
    assert resp.json()["status"] == "maintenance"

    payload = {
        "vehicle_id": "v-003",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 10.0,
        "heading": 90.0,
        "fuel_level": 50.0,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
    assert resp.status_code == 200

    resp = client.get("/api/v1/vehicles/v-003", headers=auth_headers)
    assert resp.json()["status"] == "maintenance"


def test_ingest_telemetry_activates_idle_vehicle(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    payload = {
        "vehicle_id": "v-002",
        "latitude": 37.3382,
        "longitude": -121.8863,
        "speed_kmh": 30.0,
        "heading": 45.0,
        "fuel_level": 60.0,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
    assert resp.status_code == 200

    resp = client.get("/api/v1/vehicles/v-002", headers=auth_headers)
    assert resp.json()["status"] == "active"


def test_ingest_telemetry_no_auth(client: TestClient) -> None:
    payload = {
        "vehicle_id": "v-001",
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 55.0,
        "heading": 180.0,
        "fuel_level": 72.5,
        "timestamp": "2024-01-15T12:00:00Z",
    }
    resp = client.post("/api/v1/telemetry/", json=payload)
    assert resp.status_code == 403
