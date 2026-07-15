"""Geofence evaluation for incoming vehicle telemetry."""

from __future__ import annotations

import time
from datetime import datetime
from typing import Any

from src.api.db import (
    delete_zone_presence,
    get_zone_presence,
    insert_alert,
    insert_zone_event,
    insert_zone_presence,
    list_zones,
)
from src.geo import haversine_m

ACTIVE_ZONE_CACHE_TTL_SECONDS = 30.0
_active_zones_cache: list[dict[str, Any]] | None = None
_active_zones_cache_expires_at = 0.0


def invalidate_active_zones_cache() -> None:
    """Clear the cached active zones after a zone mutation."""
    global _active_zones_cache, _active_zones_cache_expires_at
    _active_zones_cache = None
    _active_zones_cache_expires_at = 0.0


def _get_active_zones() -> list[dict[str, Any]]:
    global _active_zones_cache, _active_zones_cache_expires_at
    now = time.monotonic()
    if _active_zones_cache is None or now >= _active_zones_cache_expires_at:
        _active_zones_cache = list_zones(active=True)
        _active_zones_cache_expires_at = now + ACTIVE_ZONE_CACHE_TTL_SECONDS
    return _active_zones_cache


def evaluate_telemetry(
    vehicle_id: str,
    latitude: float,
    longitude: float,
    timestamp: datetime,
) -> None:
    """Evaluate one telemetry point against all active geofence zones."""
    occurred_at = timestamp.isoformat()
    for zone in _get_active_zones():
        distance_m = haversine_m(
            latitude,
            longitude,
            zone["center_latitude"],
            zone["center_longitude"],
        )
        inside = distance_m <= zone["radius_m"]
        presence = get_zone_presence(vehicle_id, zone["id"])

        if presence is None and inside:
            insert_zone_presence(vehicle_id, zone["id"], occurred_at)
            event = insert_zone_event(
                vehicle_id=vehicle_id,
                zone_id=zone["id"],
                event_type="entry",
                latitude=latitude,
                longitude=longitude,
                occurred_at=occurred_at,
            )
            if zone["zone_type"] == "restricted":
                insert_alert(
                    zone_event_id=event["id"],
                    vehicle_id=vehicle_id,
                    zone_id=zone["id"],
                )
        elif presence is not None and not inside:
            delete_zone_presence(vehicle_id, zone["id"])
            insert_zone_event(
                vehicle_id=vehicle_id,
                zone_id=zone["id"],
                event_type="exit",
                latitude=latitude,
                longitude=longitude,
                occurred_at=occurred_at,
            )
