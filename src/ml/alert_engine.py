"""Evaluation engine that matches telemetry snapshots against alert rules."""

from __future__ import annotations

import logging
from typing import Any, Callable

from src.api.alert_store import list_rules, record_alert

logger = logging.getLogger(__name__)

SUPPORTED_METRICS = frozenset({"fuel_level", "speed_kmh"})

_OPERATORS: dict[str, Callable[[float, float], bool]] = {
    "lt": lambda value, threshold: value < threshold,
    "lte": lambda value, threshold: value <= threshold,
    "gt": lambda value, threshold: value > threshold,
    "gte": lambda value, threshold: value >= threshold,
}


def rule_matches(rule: dict[str, Any], snapshot: dict[str, Any]) -> bool:
    """Return True when a telemetry snapshot violates the rule's threshold."""
    metric = rule["metric"]
    if metric not in snapshot:
        return False
    compare = _OPERATORS.get(rule["operator"])
    if compare is None:
        logger.warning("Unknown operator %r on rule %s", rule["operator"], rule["id"])
        return False
    return compare(float(snapshot[metric]), float(rule["threshold"]))


def evaluate_snapshot(
    vehicle_id: str,
    snapshot: dict[str, Any],
    rules: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Evaluate one vehicle's latest telemetry against enabled rules.

    Returns the fired alert rows (already persisted). Rules may be passed in
    to avoid refetching when evaluating many vehicles in one sweep.
    """
    if rules is None:
        rules = list_rules(enabled_only=True)

    fired: list[dict[str, Any]] = []
    for rule in rules:
        if not rule_matches(rule, snapshot):
            continue
        alert = record_alert(
            rule_id=rule["id"],
            vehicle_id=vehicle_id,
            metric_value=float(snapshot[rule["metric"]]),
            severity=rule["severity"],
        )
        fired.append(alert)
        logger.info(
            "Alert fired: rule=%s vehicle=%s %s=%s",
            rule["id"], vehicle_id, rule["metric"], snapshot[rule["metric"]],
        )
    return fired


def evaluate_fleet(snapshots: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    """Evaluate a batch of vehicle snapshots with a single rule fetch."""
    rules = list_rules(enabled_only=True)
    fired: list[dict[str, Any]] = []
    for vehicle_id, snapshot in snapshots.items():
        fired.extend(evaluate_snapshot(vehicle_id, snapshot, rules=rules))
    return fired
