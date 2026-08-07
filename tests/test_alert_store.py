from __future__ import annotations

from src.api import alert_store


def _make_rule(**overrides: object) -> dict:
    kwargs: dict = {
        "name": "Low fuel",
        "metric": "fuel_level",
        "operator": "lt",
        "threshold": 15.0,
        "severity": "warning",
        "created_by": "op-001",
    }
    kwargs.update(overrides)
    return alert_store.create_rule(**kwargs)


def test_create_rule_persists_fields():
    rule = _make_rule(name="Overheat", metric="speed_kmh", operator="gt", threshold=110.0)
    assert rule["id"].startswith("rule-")
    assert rule["name"] == "Overheat"
    assert rule["metric"] == "speed_kmh"
    assert rule["operator"] == "gt"
    assert rule["threshold"] == 110.0
    assert rule["enabled"] == 1


def test_list_rules_enabled_only_filters_disabled():
    rule = _make_rule(name="Disabled rule")
    alert_store.set_rule_enabled(rule["id"], False)
    enabled_ids = [r["id"] for r in alert_store.list_rules(enabled_only=True)]
    all_ids = [r["id"] for r in alert_store.list_rules()]
    assert rule["id"] not in enabled_ids
    assert rule["id"] in all_ids


def test_record_and_acknowledge_alert():
    rule = _make_rule(name="Ack test")
    alert = alert_store.record_alert(rule["id"], "v-001", 9.5, "critical")
    assert alert["acknowledged"] == 0

    acked = alert_store.acknowledge_alert(alert["id"])
    assert acked is not None
    assert acked["acknowledged"] == 1


def test_list_alerts_filters_by_vehicle_and_ack():
    rule = _make_rule(name="Filter test")
    alert_store.record_alert(rule["id"], "v-777", 3.0, "warning")
    acked = alert_store.record_alert(rule["id"], "v-777", 2.0, "warning")
    alert_store.acknowledge_alert(acked["id"])

    for_vehicle = alert_store.list_alerts(vehicle_id="v-777")
    assert len(for_vehicle) == 2

    open_only = alert_store.list_alerts(vehicle_id="v-777", unacknowledged_only=True)
    assert len(open_only) == 1
    assert open_only[0]["acknowledged"] == 0


def test_delete_rule_removes_rule_and_alerts():
    rule = _make_rule(name="Delete me")
    alert_store.record_alert(rule["id"], "v-888", 1.0, "warning")
    alert_store.delete_rule(rule["id"])
    assert alert_store.get_rule(rule["id"]) is None
    assert alert_store.list_alerts(vehicle_id="v-888") == []
