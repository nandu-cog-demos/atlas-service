from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.auth import create_token


def _create_alert(
    client: TestClient,
    auth_headers: dict[str, str],
    name: str,
    timestamp: str,
) -> str:
    zone_response = client.post(
        "/api/v1/zones/",
        json={
            "name": name,
            "center_latitude": 37.7749,
            "center_longitude": -122.4194,
            "radius_m": 250.0,
            "zone_type": "restricted",
        },
        headers=auth_headers,
    )
    assert zone_response.status_code == 200
    zone_id = zone_response.json()["id"]

    telemetry_response = client.post(
        "/api/v1/telemetry/",
        json={
            "vehicle_id": "v-001",
            "latitude": 37.7749,
            "longitude": -122.4194,
            "speed_kmh": 35.0,
            "heading": 180.0,
            "fuel_level": 80.0,
            "timestamp": timestamp,
        },
        headers=auth_headers,
    )
    assert telemetry_response.status_code == 200

    alerts_response = client.get(
        "/api/v1/alerts/?acknowledged=false&limit=100",
        headers=auth_headers,
    )
    assert alerts_response.status_code == 200
    matching = [alert for alert in alerts_response.json() if alert["zone_id"] == zone_id]
    assert len(matching) == 1
    return matching[0]["id"]


def test_list_alerts_newest_first(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    first_id = _create_alert(
        client,
        auth_headers,
        "First alert",
        "2024-03-01T10:00:00Z",
    )
    second_id = _create_alert(
        client,
        auth_headers,
        "Second alert",
        "2024-03-01T10:01:00Z",
    )

    response = client.get("/api/v1/alerts/?limit=100", headers=auth_headers)

    assert response.status_code == 200
    ids = [alert["id"] for alert in response.json()]
    assert ids.index(second_id) < ids.index(first_id)


def test_list_alerts_acknowledged_filter(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    acknowledged_id = _create_alert(
        client,
        auth_headers,
        "Acknowledged alert",
        "2024-03-02T10:00:00Z",
    )
    unacknowledged_id = _create_alert(
        client,
        auth_headers,
        "Unacknowledged alert",
        "2024-03-02T10:01:00Z",
    )
    acknowledge_response = client.post(
        f"/api/v1/alerts/{acknowledged_id}/acknowledge",
        headers=auth_headers,
    )
    assert acknowledge_response.status_code == 200

    acknowledged_response = client.get(
        "/api/v1/alerts/?acknowledged=true&limit=100",
        headers=auth_headers,
    )
    unacknowledged_response = client.get(
        "/api/v1/alerts/?acknowledged=false&limit=100",
        headers=auth_headers,
    )

    acknowledged_ids = {alert["id"] for alert in acknowledged_response.json()}
    unacknowledged_ids = {alert["id"] for alert in unacknowledged_response.json()}
    assert acknowledged_id in acknowledged_ids
    assert acknowledged_id not in unacknowledged_ids
    assert unacknowledged_id in unacknowledged_ids


def test_acknowledge_sets_operator_and_timestamp(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    alert_id = _create_alert(
        client,
        auth_headers,
        "Acknowledge alert",
        "2024-03-03T10:00:00Z",
    )

    response = client.post(
        f"/api/v1/alerts/{alert_id}/acknowledge",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert data["id"] == alert_id
    assert data["acknowledged"] is True
    assert data["acknowledged_by"] == "op-001"
    assert data["acknowledged_at"] is not None


def test_acknowledge_is_idempotent(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    alert_id = _create_alert(
        client,
        auth_headers,
        "Idempotent alert",
        "2024-03-04T10:00:00Z",
    )

    first_response = client.post(
        f"/api/v1/alerts/{alert_id}/acknowledge",
        headers=auth_headers,
    )
    second_response = client.post(
        f"/api/v1/alerts/{alert_id}/acknowledge",
        headers={"Authorization": f"Bearer {create_token('op-002')}"},
    )

    first_data = first_response.json()
    second_data = second_response.json()
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert second_data["acknowledged_by"] == first_data["acknowledged_by"]
    assert second_data["acknowledged_at"] == first_data["acknowledged_at"]


def test_acknowledge_unknown_alert(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    response = client.post(
        "/api/v1/alerts/does-not-exist/acknowledge",
        headers=auth_headers,
    )

    assert response.status_code == 404


def test_alerts_require_auth(client: TestClient) -> None:
    list_response = client.get("/api/v1/alerts/")
    acknowledge_response = client.post("/api/v1/alerts/does-not-exist/acknowledge")

    assert list_response.status_code == 403
    assert acknowledge_response.status_code == 403
