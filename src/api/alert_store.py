"""Persistence helpers for maintenance alert rules and fired alerts."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.api.db import _get_connection, execute, fetch_all, fetch_one

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS alert_rules (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    metric TEXT NOT NULL,
    operator TEXT NOT NULL,
    threshold REAL NOT NULL,
    severity TEXT NOT NULL DEFAULT 'warning',
    enabled INTEGER NOT NULL DEFAULT 1,
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS alerts (
    id TEXT PRIMARY KEY,
    rule_id TEXT NOT NULL,
    vehicle_id TEXT NOT NULL,
    metric_value REAL NOT NULL,
    severity TEXT NOT NULL,
    acknowledged INTEGER NOT NULL DEFAULT 0,
    fired_at TEXT NOT NULL,
    FOREIGN KEY (rule_id) REFERENCES alert_rules(id)
);
"""

_schema_ready = False


def ensure_schema() -> None:
    global _schema_ready
    if _schema_ready:
        return
    conn: sqlite3.Connection = _get_connection()
    conn.executescript(SCHEMA)
    conn.commit()
    _schema_ready = True


def create_rule(
    name: str,
    metric: str,
    operator: str,
    threshold: float,
    severity: str,
    created_by: str,
) -> dict[str, Any]:
    ensure_schema()
    rule_id = f"rule-{uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO alert_rules
            (id, name, metric, operator, threshold, severity, enabled, created_by, created_at)
        VALUES (?, ?, ?, ?, ?, ?, 1, ?, ?)
        """,
        (rule_id, name, metric, operator, threshold, severity, created_by, created_at),
    )
    row = fetch_one("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))
    assert row is not None
    return row


def list_rules(enabled_only: bool = False) -> list[dict[str, Any]]:
    ensure_schema()
    if enabled_only:
        return fetch_all("SELECT * FROM alert_rules WHERE enabled = 1 ORDER BY created_at")
    return fetch_all("SELECT * FROM alert_rules ORDER BY created_at")


def get_rule(rule_id: str) -> dict[str, Any] | None:
    ensure_schema()
    return fetch_one("SELECT * FROM alert_rules WHERE id = ?", (rule_id,))


def set_rule_enabled(rule_id: str, enabled: bool) -> None:
    ensure_schema()
    execute(
        "UPDATE alert_rules SET enabled = ? WHERE id = ?",
        (1 if enabled else 0, rule_id),
    )


def delete_rule(rule_id: str) -> None:
    ensure_schema()
    execute("DELETE FROM alerts WHERE rule_id = ?", (rule_id,))
    execute("DELETE FROM alert_rules WHERE id = ?", (rule_id,))


def record_alert(
    rule_id: str,
    vehicle_id: str,
    metric_value: float,
    severity: str,
) -> dict[str, Any]:
    ensure_schema()
    alert_id = str(uuid4())
    execute(
        """
        INSERT INTO alerts (id, rule_id, vehicle_id, metric_value, severity, acknowledged, fired_at)
        VALUES (?, ?, ?, ?, ?, 0, ?)
        """,
        (
            alert_id, rule_id, vehicle_id, metric_value, severity,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    row = fetch_one("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    assert row is not None
    return row


def list_alerts(
    vehicle_id: str | None = None,
    unacknowledged_only: bool = False,
    limit: int = 100,
) -> list[dict[str, Any]]:
    ensure_schema()
    clauses: list[str] = []
    params: list[Any] = []
    if vehicle_id is not None:
        clauses.append("vehicle_id = ?")
        params.append(vehicle_id)
    if unacknowledged_only:
        clauses.append("acknowledged = 0")
    where = f" WHERE {' AND '.join(clauses)}" if clauses else ""
    params.append(limit)
    return fetch_all(
        "SELECT * FROM alerts" + where + " ORDER BY fired_at DESC LIMIT ?",
        tuple(params),
    )


def acknowledge_alert(alert_id: str) -> dict[str, Any] | None:
    ensure_schema()
    execute("UPDATE alerts SET acknowledged = 1 WHERE id = ?", (alert_id,))
    return fetch_one("SELECT * FROM alerts WHERE id = ?", (alert_id,))
