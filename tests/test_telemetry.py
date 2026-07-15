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


def test_ingest_telemetry_batch(client: TestClient, auth_headers: dict[str, str]) -> None:
    payload = {
        "records": [
            {
                "vehicle_id": "v-001",
                "latitude": 37.8,
                "longitude": -122.4,
                "speed_kmh": 50.0,
                "heading": 180.0,
                "fuel_level": 70.0,
                "timestamp": "2024-01-15T12:00:00Z",
            },
            {
                "vehicle_id": "v-002",
                "latitude": 37.4,
                "longitude": -121.9,
                "speed_kmh": 40.0,
                "heading": 90.0,
                "fuel_level": 65.0,
                "timestamp": "2024-01-15T12:01:00Z",
            },
        ],
    }
    resp = client.post("/api/v1/telemetry/batch", json=payload, headers=auth_headers)

    assert resp.status_code == 200
    data = resp.json()
    assert len(data["ids"]) == 2
    assert all(data["ids"])
    assert "received_at" in data
