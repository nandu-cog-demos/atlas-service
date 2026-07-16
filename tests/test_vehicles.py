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


def test_get_vehicle_telemetry_negative_limit(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry?limit=-1", headers=auth_headers)
    assert resp.status_code == 422


def test_get_vehicle_telemetry_zero_limit(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry?limit=0", headers=auth_headers)
    assert resp.status_code == 422


def test_get_vehicle_telemetry_excessive_limit(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.get("/api/v1/vehicles/v-001/telemetry?limit=99999999", headers=auth_headers)
    assert resp.status_code == 422
