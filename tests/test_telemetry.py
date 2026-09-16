from __future__ import annotations

import sqlite3
from datetime import datetime, timezone

import pytest
from fastapi.testclient import TestClient

from src.api.db import get_recent_telemetry, insert_telemetry


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


def test_ingest_telemetry_unknown_vehicle(client: TestClient, auth_headers: dict[str, str]) -> None:
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
    assert resp.json()["detail"] == "Vehicle not found"
    assert get_recent_telemetry("v-does-not-exist") == []


def test_foreign_keys_enforced_at_db_level() -> None:
    with pytest.raises(sqlite3.IntegrityError):
        insert_telemetry(
            vehicle_id="v-does-not-exist",
            latitude=37.7749,
            longitude=-122.4194,
            speed_kmh=55.0,
            heading=180.0,
            fuel_level=72.5,
            timestamp=datetime(2024, 1, 15, 12, 0, tzinfo=timezone.utc),
        )
    assert get_recent_telemetry("v-does-not-exist") == []


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
