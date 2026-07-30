from __future__ import annotations

from src.api import alert_store
from src.ml import alert_engine


def _rule(**overrides: object) -> dict:
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


def test_rule_matches_each_operator():
    snapshot = {"fuel_level": 10.0}
    assert alert_engine.rule_matches(_rule(operator="lt", threshold=15.0), snapshot)
    assert alert_engine.rule_matches(_rule(operator="lte", threshold=10.0), snapshot)
    assert alert_engine.rule_matches(_rule(operator="gt", threshold=5.0), snapshot)
    assert alert_engine.rule_matches(_rule(operator="gte", threshold=10.0), snapshot)
    assert not alert_engine.rule_matches(_rule(operator="lt", threshold=10.0), snapshot)


def test_rule_matches_ignores_missing_metric():
    rule = _rule(metric="speed_kmh", operator="gt", threshold=100.0)
    assert not alert_engine.rule_matches(rule, {"fuel_level": 50.0})


def test_evaluate_snapshot_persists_fired_alerts():
    rule = _rule(name="Engine fire", operator="lt", threshold=20.0, severity="critical")
    fired = alert_engine.evaluate_snapshot("v-100", {"fuel_level": 12.0}, rules=[rule])
    assert len(fired) == 1
    assert fired[0]["severity"] == "critical"
    stored = alert_store.list_alerts(vehicle_id="v-100")
    assert stored[0]["rule_id"] == rule["id"]
    assert stored[0]["metric_value"] == 12.0


def test_evaluate_snapshot_skips_disabled_rules():
    rule = _rule(name="Disabled")
    alert_store.set_rule_enabled(rule["id"], False)
    fired = alert_engine.evaluate_snapshot("v-101", {"fuel_level": 1.0})
    assert rule["id"] not in [a["rule_id"] for a in fired]


def test_evaluate_fleet_evaluates_all_snapshots():
    rule = _rule(name="Fleet sweep", metric="speed_kmh", operator="gt", threshold=90.0)
    fired = alert_engine.evaluate_fleet(
        {
            "v-200": {"speed_kmh": 120.0},
            "v-201": {"speed_kmh": 40.0},
            "v-202": {"speed_kmh": 95.0},
        }
    )
    mine = [a for a in fired if a["rule_id"] == rule["id"]]
    assert sorted(a["vehicle_id"] for a in mine) == ["v-200", "v-202"]
