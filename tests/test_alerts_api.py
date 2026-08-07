from __future__ import annotations

from fastapi.testclient import TestClient


def _create_rule(client: TestClient, auth_headers: dict[str, str], **overrides: object) -> dict:
    body = {
        "name": "Low fuel",
        "metric": "fuel_level",
        "operator": "lt",
        "threshold": 15.0,
        "severity": "warning",
    }
    body.update(overrides)
    resp = client.post("/api/v1/alerts/rules", json=body, headers=auth_headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


def test_create_rule_rejects_unsupported_metric(client, auth_headers):
    resp = client.post(
        "/api/v1/alerts/rules",
        json={
            "name": "Bad metric",
            "metric": "tire_pressure",
            "operator": "lt",
            "threshold": 30.0,
        },
        headers=auth_headers,
    )
    assert resp.status_code == 422


def test_create_and_list_rules(client, auth_headers):
    rule = _create_rule(client, auth_headers, name="API rule")
    resp = client.get("/api/v1/alerts/rules", headers=auth_headers)
    assert resp.status_code == 200
    assert rule["id"] in [r["id"] for r in resp.json()]


def test_toggle_rule_enabled(client, auth_headers):
    rule = _create_rule(client, auth_headers, name="Toggle rule")
    resp = client.patch(
        f"/api/v1/alerts/rules/{rule['id']}/enabled?enabled=false",
        headers=auth_headers,
    )
    assert resp.status_code == 200
    assert resp.json()["enabled"] is False


def test_delete_rule_then_404(client, auth_headers):
    rule = _create_rule(client, auth_headers, name="Delete rule")
    assert (
        client.delete(f"/api/v1/alerts/rules/{rule['id']}", headers=auth_headers).status_code
        == 200
    )
    assert (
        client.delete(f"/api/v1/alerts/rules/{rule['id']}", headers=auth_headers).status_code
        == 404
    )


def test_telemetry_ingest_fires_alert_and_ack_flow(client, auth_headers):
    rule = _create_rule(
        client, auth_headers, name="Speeding", metric="speed_kmh",
        operator="gt", threshold=100.0, severity="critical",
    )

    resp = client.post(
        "/api/v1/telemetry/",
        json={
            "vehicle_id": "v-002",
            "latitude": 37.0,
            "longitude": -122.0,
            "speed_kmh": 130.0,
            "heading": 45.0,
            "fuel_level": 80.0,
            "timestamp": "2024-01-15T12:00:00Z",
        },
        headers=auth_headers,
    )
    assert resp.status_code == 200

    alerts = client.get(
        "/api/v1/alerts/?vehicle_id=v-002&unacknowledged_only=true",
        headers=auth_headers,
    ).json()
    mine = [a for a in alerts if a["rule_id"] == rule["id"]]
    assert len(mine) == 1
    assert mine[0]["severity"] == "critical"
    assert mine[0]["metric_value"] == 130.0

    acked = client.post(
        f"/api/v1/alerts/{mine[0]['id']}/acknowledge",
        headers=auth_headers,
    )
    assert acked.status_code == 200
    assert acked.json()["acknowledged"] is True
