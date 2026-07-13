from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.db import execute, get_recent_telemetry, get_vehicle


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


def test_delete_vehicle(client: TestClient, auth_headers: dict[str, str]) -> None:
    execute(
        "INSERT INTO vehicles (id, name, status) VALUES (?, ?, ?)",
        ("v-del", "Truck Delta", "idle"),
    )
    execute(
        """
        INSERT INTO telemetry
            (id, vehicle_id, latitude, longitude, speed_kmh,
             heading, fuel_level, timestamp, received_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        ("t-del", "v-del", 37.0, -122.0, 50.0, 90.0, 80.0,
         "2024-01-15T10:00:00Z", "2024-01-15T10:00:01Z"),
    )
    resp = client.delete("/api/v1/vehicles/v-del", headers=auth_headers)
    assert resp.status_code == 204
    assert get_vehicle("v-del") is None
    assert get_recent_telemetry("v-del") == []


def test_delete_vehicle_not_found(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.delete("/api/v1/vehicles/v-999", headers=auth_headers)
    assert resp.status_code == 404
    assert resp.json()["detail"] == "Vehicle not found"


def test_get_vehicle_telemetry(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry", headers=auth_headers)
    assert resp.status_code == 200
    assert isinstance(resp.json(), list)
