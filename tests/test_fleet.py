from __future__ import annotations

from fastapi.testclient import TestClient


def test_fleet_summary(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/fleet/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["total_vehicles"] >= 3
    counts = data["status_counts"]
    assert set(counts) == {"active", "idle", "maintenance", "offline"}
    assert sum(counts.values()) == data["total_vehicles"]
    assert counts["maintenance"] >= 1


def test_fleet_summary_average_fuel(client: TestClient, auth_headers: dict[str, str]) -> None:
    for fuel_level, timestamp in [(60.0, "2024-01-15T11:00:00Z"), (80.0, "2024-01-15T12:00:00Z")]:
        payload = {
            "vehicle_id": "v-002",
            "latitude": 37.3382,
            "longitude": -121.8863,
            "speed_kmh": 40.0,
            "heading": 90.0,
            "fuel_level": fuel_level,
            "timestamp": timestamp,
        }
        resp = client.post("/api/v1/telemetry/", json=payload, headers=auth_headers)
        assert resp.status_code == 200

    resp = client.get("/api/v1/fleet/summary", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["average_fuel_level"] == 80.0


def test_fleet_summary_no_auth(client: TestClient) -> None:
    resp = client.get("/api/v1/fleet/summary")
    assert resp.status_code == 403
