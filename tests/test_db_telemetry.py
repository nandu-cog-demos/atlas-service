from __future__ import annotations

import sqlite3
from datetime import datetime, timezone
from typing import Generator

import pytest

from src.api import db

_TS = datetime(2024, 1, 15, 12, 0, 0, tzinfo=timezone.utc)


@pytest.fixture(autouse=True)
def restore_vehicle_state() -> Generator[None, None, None]:
    rows = db.fetch_all("SELECT * FROM vehicles")
    yield
    for row in rows:
        db.execute(
            "UPDATE vehicles SET status = ?, last_latitude = ?,"
            " last_longitude = ?, last_seen = ? WHERE id = ?",
            (
                row["status"], row["last_latitude"], row["last_longitude"],
                row["last_seen"], row["id"],
            ),
        )


def _insert(vehicle_id: str) -> str:
    return db.insert_telemetry(
        vehicle_id=vehicle_id,
        latitude=37.7749,
        longitude=-122.4194,
        speed_kmh=55.0,
        heading=180.0,
        fuel_level=72.5,
        timestamp=_TS,
    )


def test_insert_telemetry_activates_idle_vehicle() -> None:
    _insert("v-002")
    vehicle = db.get_vehicle("v-002")
    assert vehicle is not None
    assert vehicle["status"] == "active"
    assert vehicle["last_latitude"] == 37.7749
    assert vehicle["last_longitude"] == -122.4194


def test_insert_telemetry_preserves_maintenance_status() -> None:
    _insert("v-003")
    vehicle = db.get_vehicle("v-003")
    assert vehicle is not None
    assert vehicle["status"] == "maintenance"
    assert vehicle["last_latitude"] == 37.7749
    assert vehicle["last_longitude"] == -122.4194
    assert vehicle["last_seen"] is not None


def test_insert_telemetry_preserves_offline_status() -> None:
    db.execute("UPDATE vehicles SET status = 'offline' WHERE id = ?", ("v-002",))
    _insert("v-002")
    vehicle = db.get_vehicle("v-002")
    assert vehicle is not None
    assert vehicle["status"] == "offline"


def test_insert_telemetry_is_atomic_on_update_failure() -> None:
    db.execute(
        """
        CREATE TRIGGER fail_vehicle_update
        BEFORE UPDATE ON vehicles
        WHEN NEW.id = 'v-001'
        BEGIN
            SELECT RAISE(ABORT, 'simulated failure');
        END
        """
    )
    before = len(db.get_recent_telemetry("v-001", limit=1000))
    try:
        with pytest.raises(sqlite3.DatabaseError):
            _insert("v-001")
    finally:
        db.execute("DROP TRIGGER fail_vehicle_update")
    after = len(db.get_recent_telemetry("v-001", limit=1000))
    assert after == before
