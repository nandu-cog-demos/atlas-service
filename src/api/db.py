"""Database query helpers. All queries MUST use parameterized placeholders."""

from __future__ import annotations

import logging
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from typing import Any, Generator
from uuid import uuid4

from src.api.models import TelemetryPayload

logger = logging.getLogger(__name__)

_DB_PATH = ":memory:"
_connection: sqlite3.Connection | None = None
_db_lock = threading.RLock()


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

        CREATE INDEX IF NOT EXISTS idx_telemetry_vehicle_ts
            ON telemetry (vehicle_id, timestamp DESC);

        CREATE TABLE IF NOT EXISTS operators (
            id TEXT PRIMARY KEY,
            display_name TEXT NOT NULL,
            theme TEXT NOT NULL DEFAULT 'system',
            notifications_enabled INTEGER NOT NULL DEFAULT 1,
            default_map_zoom INTEGER NOT NULL DEFAULT 12
        );

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
    with _db_lock:
        conn = _get_connection()
        cursor = conn.cursor()
        try:
            yield cursor
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            cursor.close()


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
    with get_cursor() as cur:
        cur.execute(
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
        cur.execute(
            "UPDATE vehicles SET last_latitude = ?, last_longitude = ?,"
            " last_seen = ?, status = 'active' WHERE id = ?",
            (latitude, longitude, now, vehicle_id),
        )
    return record_id


def insert_telemetry_batch(records: list[TelemetryPayload]) -> list[str]:
    record_ids = [str(uuid4()) for _ in records]
    received_at = [datetime.now(timezone.utc).isoformat() for _ in records]
    rows = [
        (
            record_id,
            record.vehicle_id,
            record.latitude,
            record.longitude,
            record.speed_kmh,
            record.heading,
            record.fuel_level,
            record.timestamp.isoformat(),
            received,
        )
        for record_id, received, record in zip(record_ids, received_at, records)
    ]

    latest_by_vehicle: dict[str, tuple[TelemetryPayload, str]] = {}
    for record, received in zip(records, received_at):
        latest = latest_by_vehicle.get(record.vehicle_id)
        if latest is None or record.timestamp > latest[0].timestamp:
            latest_by_vehicle[record.vehicle_id] = (record, received)

    with get_cursor() as cur:
        cur.executemany(
            """
            INSERT INTO telemetry
                (id, vehicle_id, latitude, longitude, speed_kmh,
                 heading, fuel_level, timestamp, received_at)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            rows,
        )
        for vehicle_id, (record, received) in latest_by_vehicle.items():
            cur.execute(
                "UPDATE vehicles SET last_latitude = ?, last_longitude = ?,"
                " last_seen = ?, status = 'active' WHERE id = ?",
                (record.latitude, record.longitude, received, vehicle_id),
            )
    return record_ids


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
