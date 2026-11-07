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


def _telemetry(vehicle_id: str, fuel_level: float) -> dict:
    return {
        "vehicle_id": vehicle_id,
        "latitude": 37.7749,
        "longitude": -122.4194,
        "speed_kmh": 40.0,
        "heading": 90.0,
        "fuel_level": fuel_level,
        "timestamp": "2024-01-15T12:00:00Z",
    }


def test_vehicles_report_fuel_and_low_fuel_flag(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    data = {v["id"]: v for v in client.get("/api/v1/vehicles/", headers=auth_headers).json()}
    assert data["v-002"]["fuel_level"] == 11.0
    assert data["v-002"]["low_fuel"] is True
    assert data["v-003"]["fuel_level"] is None
    assert data["v-003"]["low_fuel"] is False


def test_low_fuel_flag_follows_latest_telemetry(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    client.post("/api/v1/telemetry/", json=_telemetry("v-001", 8.0), headers=auth_headers)
    detail = client.get("/api/v1/vehicles/v-001", headers=auth_headers).json()
    assert detail["fuel_level"] == 8.0
    assert detail["low_fuel"] is True

    client.post("/api/v1/telemetry/", json=_telemetry("v-001", 72.5), headers=auth_headers)
    detail = client.get("/api/v1/vehicles/v-001", headers=auth_headers).json()
    assert detail["fuel_level"] == 72.5
    assert detail["low_fuel"] is False


def test_low_fuel_threshold_is_configurable(
    client: TestClient, auth_headers: dict[str, str], monkeypatch
) -> None:
    from src.api.routes import vehicles

    monkeypatch.setattr(vehicles, "LOW_FUEL_THRESHOLD_PCT", 5.0)
    detail = client.get("/api/v1/vehicles/v-002", headers=auth_headers).json()
    assert detail["low_fuel"] is False
