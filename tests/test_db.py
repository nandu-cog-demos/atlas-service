from __future__ import annotations

from datetime import datetime, timezone

from src.api.db import (
    get_cursor,
    get_vehicle,
    insert_telemetry,
    insert_telemetry_batch,
)
from src.api.models import TelemetryPayload


def test_insert_telemetry_updates_vehicle_in_one_transaction() -> None:
    timestamp = datetime(2024, 1, 15, 13, 0, tzinfo=timezone.utc)
    record_id = insert_telemetry(
        vehicle_id="v-001",
        latitude=38.0,
        longitude=-123.0,
        speed_kmh=45.0,
        heading=90.0,
        fuel_level=60.0,
        timestamp=timestamp,
    )

    with get_cursor() as cur:
        cur.execute("SELECT id FROM telemetry WHERE id = ?", (record_id,))
        assert cur.fetchone()["id"] == record_id
    vehicle = get_vehicle("v-001")
    assert vehicle is not None
    assert vehicle["last_latitude"] == 38.0
    assert vehicle["last_longitude"] == -123.0
    assert vehicle["last_seen"] is not None


def test_telemetry_vehicle_timestamp_index_exists() -> None:
    with get_cursor() as cur:
        cur.execute("PRAGMA index_list('telemetry')")
        indexes = {row["name"] for row in cur.fetchall()}

    assert "idx_telemetry_vehicle_ts" in indexes


def test_insert_telemetry_batch_updates_each_vehicle_from_latest_record() -> None:
    records = [
        TelemetryPayload(
            vehicle_id="v-003",
            latitude=36.0,
            longitude=-122.0,
            speed_kmh=30.0,
            heading=45.0,
            fuel_level=50.0,
            timestamp=datetime(2024, 1, 15, 14, 0, tzinfo=timezone.utc),
        ),
        TelemetryPayload(
            vehicle_id="v-003",
            latitude=36.1,
            longitude=-122.1,
            speed_kmh=35.0,
            heading=50.0,
            fuel_level=49.0,
            timestamp=datetime(2024, 1, 15, 14, 1, tzinfo=timezone.utc),
        ),
    ]

    record_ids = insert_telemetry_batch(records)

    assert len(record_ids) == 2
    assert all(record_ids)
    vehicle = get_vehicle("v-003")
    assert vehicle is not None
    assert vehicle["last_latitude"] == 36.1
    assert vehicle["last_longitude"] == -122.1
    assert vehicle["last_seen"] is not None
