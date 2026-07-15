from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.db import list_alerts, list_zone_events


def _zone_payload(
    name: str,
    zone_type: str = "site",
) -> dict[str, object]:
    return {
        "name": name,
        "center_latitude": 37.7749,
        "center_longitude": -122.4194,
        "radius_m": 250.0,
        "zone_type": zone_type,
    }


def _telemetry_payload(latitude: float, timestamp: str) -> dict[str, object]:
    return {
        "vehicle_id": "v-001",
        "latitude": latitude,
        "longitude": -122.4194,
        "speed_kmh": 35.0,
        "heading": 180.0,
        "fuel_level": 80.0,
        "timestamp": timestamp,
    }


def _create_zone(
    client: TestClient,
    auth_headers: dict[str, str],
    name: str,
    zone_type: str = "site",
) -> str:
    response = client.post(
        "/api/v1/zones/",
        json=_zone_payload(name, zone_type),
        headers=auth_headers,
    )
    assert response.status_code == 200
    return response.json()["id"]


def _post_telemetry(
    client: TestClient,
    auth_headers: dict[str, str],
    latitude: float,
    timestamp: str,
) -> None:
    response = client.post(
        "/api/v1/telemetry/",
        json=_telemetry_payload(latitude, timestamp),
        headers=auth_headers,
    )
    assert response.status_code == 200


def test_entry_and_exit_crossings(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "Entry exit site")

    _post_telemetry(client, auth_headers, 37.7800, "2024-02-01T10:00:00Z")
    _post_telemetry(client, auth_headers, 37.7749, "2024-02-01T10:01:00Z")
    _post_telemetry(client, auth_headers, 37.7800, "2024-02-01T10:02:00Z")

    events = list_zone_events(vehicle_id="v-001", zone_id=zone_id)
    assert [event["event_type"] for event in events] == ["exit", "entry"]


def test_remaining_inside_has_no_duplicate_event_or_alert(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "Restricted duplicate", "restricted")

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-02T10:00:00Z")
    _post_telemetry(client, auth_headers, 37.7749, "2024-02-02T10:01:00Z")

    events = list_zone_events(vehicle_id="v-001", zone_id=zone_id)
    alerts = list_alerts(vehicle_id="v-001", zone_id=zone_id)
    assert len(events) == 1
    assert events[0]["event_type"] == "entry"
    assert len(alerts) == 1
    assert alerts[0]["zone_event_id"] == events[0]["id"]


def test_first_report_inside_counts_as_entry(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "First report site")

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-03T10:00:00Z")

    events = list_zone_events(vehicle_id="v-001", zone_id=zone_id)
    assert len(events) == 1
    assert events[0]["event_type"] == "entry"


def test_restricted_entry_creates_exactly_one_alert(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "Restricted alert", "restricted")

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-04T10:00:00Z")
    _post_telemetry(client, auth_headers, 37.7749, "2024-02-04T10:01:00Z")

    alerts = list_alerts(vehicle_id="v-001", zone_id=zone_id)
    assert len(alerts) == 1
    assert alerts[0]["acknowledged"] == 0


def test_site_entry_does_not_create_alert(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "Site no alert")

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-05T10:00:00Z")

    assert len(list_zone_events(vehicle_id="v-001", zone_id=zone_id)) == 1
    assert list_alerts(vehicle_id="v-001", zone_id=zone_id) == []


def test_deactivated_zone_is_not_evaluated(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    zone_id = _create_zone(client, auth_headers, "Deactivated site")
    response = client.delete(f"/api/v1/zones/{zone_id}", headers=auth_headers)
    assert response.status_code == 200

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-06T10:00:00Z")

    assert list_zone_events(vehicle_id="v-001", zone_id=zone_id) == []


def test_zone_events_endpoint_filters(
    client: TestClient,
    auth_headers: dict[str, str],
) -> None:
    first_zone_id = _create_zone(client, auth_headers, "Events first")
    second_zone_id = _create_zone(client, auth_headers, "Events second")

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-07T10:00:00Z")
    first_events = list_zone_events(vehicle_id="v-001", zone_id=first_zone_id)
    assert first_events

    _post_telemetry(client, auth_headers, 37.7749, "2024-02-07T10:01:00Z")
    second_events = list_zone_events(vehicle_id="v-001", zone_id=second_zone_id)
    assert second_events

    response = client.get(
        f"/api/v1/zone-events/?vehicle_id=v-001&zone_id={first_zone_id}&limit=1",
        headers=auth_headers,
    )

    assert response.status_code == 200
    data = response.json()
    assert len(data) == 1
    assert data[0]["id"] == first_events[0]["id"]
    assert data[0]["zone_id"] == first_zone_id
    assert all(event["zone_id"] != second_zone_id for event in data)
