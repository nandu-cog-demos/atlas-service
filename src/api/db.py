"""Database query helpers. All queries MUST use parameterized placeholders."""

from __future__ import annotations

import logging
import sqlite3
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator
from uuid import uuid4

logger = logging.getLogger(__name__)

_DB_PATH = ":memory:"
_connection: sqlite3.Connection | None = None


def _get_connection() -> sqlite3.Connection:
    global _connection
    if _connection is None:
        _connection = sqlite3.connect(_DB_PATH, check_same_thread=False)
        _connection.row_factory = sqlite3.Row
        _init_schema(_connection)
    return _connection


def _init_schema(conn: sqlite3.Connection) -> None:
    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS vehicles (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            status TEXT NOT NULL DEFAULT 'idle',
            last_latitude REAL,
            last_longitude REAL,
            last_seen TEXT
        );

        CREATE TABLE IF NOT EXISTS telemetry (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            speed_kmh REAL NOT NULL,
            heading REAL NOT NULL,
            fuel_level REAL NOT NULL,
            timestamp TEXT NOT NULL,
            received_at TEXT NOT NULL,
            FOREIGN KEY (vehicle_id) REFERENCES vehicles(id)
        );

        CREATE TABLE IF NOT EXISTS operators (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            theme TEXT NOT NULL DEFAULT 'system',
            notifications_enabled INTEGER NOT NULL DEFAULT 1,
            default_map_zoom INTEGER NOT NULL DEFAULT 12
        );

        CREATE TABLE IF NOT EXISTS zones (
            id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            center_latitude REAL NOT NULL,
            center_longitude REAL NOT NULL,
            radius_m REAL NOT NULL,
            zone_type TEXT NOT NULL CHECK (zone_type IN ('restricted', 'site')),
            active INTEGER NOT NULL DEFAULT 1,
            created_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS zone_events (
            id TEXT PRIMARY KEY,
            vehicle_id TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            event_type TEXT NOT NULL CHECK (event_type IN ('entry', 'exit')),
            latitude REAL NOT NULL,
            longitude REAL NOT NULL,
            occurred_at TEXT NOT NULL
        );

        CREATE TABLE IF NOT EXISTS vehicle_zone_presence (
            vehicle_id TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            entered_at TEXT NOT NULL,
            PRIMARY KEY (vehicle_id, zone_id)
        );

        CREATE TABLE IF NOT EXISTS alerts (
            id TEXT PRIMARY KEY,
            zone_event_id TEXT NOT NULL,
            vehicle_id TEXT NOT NULL,
            zone_id TEXT NOT NULL,
            created_at TEXT NOT NULL,
            acknowledged INTEGER NOT NULL DEFAULT 0,
            acknowledged_by TEXT,
            acknowledged_at TEXT
        );

        CREATE INDEX IF NOT EXISTS idx_zone_events_occurred_at
            ON zone_events (occurred_at);
        CREATE INDEX IF NOT EXISTS idx_alerts_created_at
            ON alerts (created_at);

        INSERT OR IGNORE INTO vehicles (id, name, status, last_latitude, last_longitude, last_seen)
        VALUES
            ('v-001', 'Truck Alpha', 'active', 37.7749, -122.4194, '2024-01-15T10:30:00Z'),
            ('v-002', 'Van Bravo', 'idle', 37.3382, -121.8863, '2024-01-15T09:15:00Z'),
            ('v-003', 'Truck Charlie', 'maintenance', NULL, NULL, NULL);

        INSERT OR IGNORE INTO operators (id, display_name)
        VALUES
            ('op-001', 'Fleet Manager'),
            ('op-002', 'Dispatcher');
        """
    )
    conn.commit()


@contextmanager
def get_cursor() -> Generator[sqlite3.Cursor, None, None]:
    conn = _get_connection()
    cursor = conn.cursor()
    try:
        yield cursor
        conn.commit()
    except Exception:
        conn.rollback()
        raise


def fetch_one(query: str, params: tuple[Any, ...] = ()) -> dict[str, Any] | None:
    with get_cursor() as cur:
        cur.execute(query, params)
        row = cur.fetchone()
        return dict(row) if row else None


def fetch_all(query: str, params: tuple[Any, ...] = ()) -> list[dict[str, Any]]:
    with get_cursor() as cur:
        cur.execute(query, params)
        return [dict(r) for r in cur.fetchall()]


def execute(query: str, params: tuple[Any, ...] = ()) -> None:
    with get_cursor() as cur:
        cur.execute(query, params)


def insert_telemetry(
    vehicle_id: str,
    latitude: float,
    longitude: float,
    speed_kmh: float,
    heading: float,
    fuel_level: float,
    timestamp: datetime,
) -> str:
    record_id = str(uuid4())
    now = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO telemetry
            (id, vehicle_id, latitude, longitude, speed_kmh,
             heading, fuel_level, timestamp, received_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            record_id, vehicle_id, latitude, longitude,
            speed_kmh, heading, fuel_level,
            timestamp.isoformat(), now,
        ),
    )
    execute(
        "UPDATE vehicles SET last_latitude = ?, last_longitude = ?,"
        " last_seen = ?, status = 'active' WHERE id = ?",
        (latitude, longitude, now, vehicle_id),
    )
    return record_id


def get_vehicle(vehicle_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM vehicles WHERE id = ?", (vehicle_id,))


def list_vehicles() -> list[dict[str, Any]]:
    return fetch_all("SELECT * FROM vehicles ORDER BY name")


def get_operator(operator_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM operators WHERE id = ?", (operator_id,))


def update_operator(operator_id: str, updates: dict[str, Any]) -> None:
    if not updates:
        return
    set_clauses = ", ".join(f"{k} = ?" for k in updates)
    values = tuple(updates.values()) + (operator_id,)
    execute(f"UPDATE operators SET {set_clauses} WHERE id = ?", values)


def get_recent_telemetry(vehicle_id: str, limit: int = 50) -> list[dict[str, Any]]:
    return fetch_all(
        "SELECT * FROM telemetry WHERE vehicle_id = ? ORDER BY timestamp DESC LIMIT ?",
        (vehicle_id, limit),
    )


def create_zone(
    name: str,
    center_latitude: float,
    center_longitude: float,
    radius_m: float,
    zone_type: str,
) -> dict[str, Any]:
    zone_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO zones
            (id, name, center_latitude, center_longitude, radius_m,
             zone_type, active, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            zone_id,
            name,
            center_latitude,
            center_longitude,
            radius_m,
            zone_type,
            1,
            created_at,
        ),
    )
    row = get_zone(zone_id)
    if row is None:
        raise RuntimeError("Zone was not created")
    from src.api.geofence import invalidate_active_zones_cache

    invalidate_active_zones_cache()
    return row


def get_zone(zone_id: str) -> dict[str, Any] | None:
    return fetch_one("SELECT * FROM zones WHERE id = ?", (zone_id,))


def list_zones(active: bool | None = None) -> list[dict[str, Any]]:
    if active is None:
        return fetch_all("SELECT * FROM zones ORDER BY created_at DESC")
    return fetch_all(
        "SELECT * FROM zones WHERE active = ? ORDER BY created_at DESC",
        (int(active),),
    )


def deactivate_zone(zone_id: str) -> dict[str, Any] | None:
    execute("UPDATE zones SET active = 0 WHERE id = ?", (zone_id,))
    row = get_zone(zone_id)
    if row is not None:
        from src.api.geofence import invalidate_active_zones_cache

        invalidate_active_zones_cache()
    return row


def get_zone_presence(vehicle_id: str, zone_id: str) -> dict[str, Any] | None:
    return fetch_one(
        """
        SELECT vehicle_id, zone_id, entered_at
        FROM vehicle_zone_presence
        WHERE vehicle_id = ? AND zone_id = ?
        """,
        (vehicle_id, zone_id),
    )


def insert_zone_presence(vehicle_id: str, zone_id: str, entered_at: str) -> None:
    execute(
        """
        INSERT INTO vehicle_zone_presence (vehicle_id, zone_id, entered_at)
        VALUES (?, ?, ?)
        """,
        (vehicle_id, zone_id, entered_at),
    )


def delete_zone_presence(vehicle_id: str, zone_id: str) -> None:
    execute(
        "DELETE FROM vehicle_zone_presence WHERE vehicle_id = ? AND zone_id = ?",
        (vehicle_id, zone_id),
    )


def insert_zone_event(
    vehicle_id: str,
    zone_id: str,
    event_type: str,
    latitude: float,
    longitude: float,
    occurred_at: str,
) -> dict[str, Any]:
    event_id = str(uuid4())
    execute(
        """
        INSERT INTO zone_events
            (id, vehicle_id, zone_id, event_type, latitude, longitude, occurred_at)
        VALUES (?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            vehicle_id,
            zone_id,
            event_type,
            latitude,
            longitude,
            occurred_at,
        ),
    )
    row = fetch_one("SELECT * FROM zone_events WHERE id = ?", (event_id,))
    if row is None:
        raise RuntimeError("Zone event was not created")
    return row


def insert_alert(zone_event_id: str, vehicle_id: str, zone_id: str) -> dict[str, Any]:
    alert_id = str(uuid4())
    created_at = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO alerts
            (id, zone_event_id, vehicle_id, zone_id, created_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        (alert_id, zone_event_id, vehicle_id, zone_id, created_at),
    )
    row = fetch_one("SELECT * FROM alerts WHERE id = ?", (alert_id,))
    if row is None:
        raise RuntimeError("Alert was not created")
    return row


def list_zone_events(
    vehicle_id: str | None = None,
    zone_id: str | None = None,
    limit: int = 50,
) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT * FROM zone_events
        WHERE (? IS NULL OR vehicle_id = ?)
          AND (? IS NULL OR zone_id = ?)
        ORDER BY occurred_at DESC
        LIMIT ?
        """,
        (vehicle_id, vehicle_id, zone_id, zone_id, limit),
    )


def list_alerts(
    vehicle_id: str | None = None,
    zone_id: str | None = None,
) -> list[dict[str, Any]]:
    return fetch_all(
        """
        SELECT * FROM alerts
        WHERE (? IS NULL OR vehicle_id = ?)
          AND (? IS NULL OR zone_id = ?)
        ORDER BY created_at DESC
        """,
        (vehicle_id, vehicle_id, zone_id, zone_id),
    )
