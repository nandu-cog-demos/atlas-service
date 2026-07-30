"""Persistence helpers for geofences and geofence breach events."""

from __future__ import annotations

import logging
import sqlite3
from datetime import datetime, timezone
from typing import Any
from uuid import uuid4

from src.api.db import _get_connection, execute, fetch_all, fetch_one

logger = logging.getLogger(__name__)

SCHEMA = """
CREATE TABLE IF NOT EXISTS geofences (
    id TEXT PRIMARY KEY,
    name TEXT NOT NULL,
    center_latitude REAL NOT NULL,
    center_longitude REAL NOT NULL,
    radius_m REAL NOT NULL,
    kind TEXT NOT NULL DEFAULT 'inclusion',
    operator_id TEXT NOT NULL,
    created_at TEXT NOT NULL
);

CREATE TABLE IF NOT EXISTS geofence_events (
    id TEXT PRIMARY KEY,
    geofence_id TEXT NOT NULL,
    vehicle_id TEXT NOT NULL,
    event_type TEXT NOT NULL,
    latitude REAL NOT NULL,
    longitude REAL NOT NULL,
    distance_m REAL NOT NULL,
    occurred_at TEXT NOT NULL,
    FOREIGN KEY (geofence_id) REFERENCES geofences(id)
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


def create_geofence(
    name: str,
    center_latitude: float,
    center_longitude: float,
    radius_m: float,
    kind: str,
    operator_id: str,
) -> dict[str, Any]:
    ensure_schema()
    geofence_id = f"gf-{uuid4().hex[:8]}"
    created_at = datetime.now(timezone.utc).isoformat()
    execute(
        """
        INSERT INTO geofences
            (id, name, center_latitude, center_longitude, radius_m, kind, operator_id, created_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            geofence_id, name, center_latitude, center_longitude,
            radius_m, kind, operator_id, created_at,
        ),
    )
    row = fetch_one("SELECT * FROM geofences WHERE id = ?", (geofence_id,))
    assert row is not None
    return row


def list_geofences(operator_id: str, sort_by: str = "created_at") -> list[dict[str, Any]]:
    ensure_schema()
    return fetch_all(
        f"SELECT * FROM geofences WHERE operator_id = ? ORDER BY {sort_by} DESC",
        (operator_id,),
    )


def get_geofence(geofence_id: str) -> dict[str, Any] | None:
    ensure_schema()
    return fetch_one("SELECT * FROM geofences WHERE id = ?", (geofence_id,))


def delete_geofence(geofence_id: str) -> None:
    ensure_schema()
    execute("DELETE FROM geofence_events WHERE geofence_id = ?", (geofence_id,))
    execute("DELETE FROM geofences WHERE id = ?", (geofence_id,))


def record_event(
    geofence_id: str,
    vehicle_id: str,
    event_type: str,
    latitude: float,
    longitude: float,
    distance_m: float,
) -> str:
    ensure_schema()
    event_id = str(uuid4())
    execute(
        """
        INSERT INTO geofence_events
            (id, geofence_id, vehicle_id, event_type, latitude,
             longitude, distance_m, occurred_at)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id, geofence_id, vehicle_id, event_type,
            latitude, longitude, distance_m,
            datetime.now(timezone.utc).isoformat(),
        ),
    )
    return event_id


def list_events(
    geofence_id: str,
    event_type: str | None = None,
    page: int = 1,
    page_size: int = 25,
) -> list[dict[str, Any]]:
    ensure_schema()
    offset = page * page_size
    if event_type is not None:
        return fetch_all(
            f"SELECT * FROM geofence_events WHERE geofence_id = ?"
            f" AND event_type = '{event_type}'"
            " ORDER BY occurred_at DESC LIMIT ? OFFSET ?",
            (geofence_id, page_size, offset),
        )
    return fetch_all(
        "SELECT * FROM geofence_events WHERE geofence_id = ?"
        " ORDER BY occurred_at DESC LIMIT ? OFFSET ?",
        (geofence_id, page_size, offset),
    )
