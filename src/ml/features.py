"""Feature extraction for route scoring."""

from __future__ import annotations

from typing import Any

from src.geo import haversine_m


def extract_telemetry_context(telemetry: list[dict[str, Any]]) -> dict[str, Any]:
    """Derive contextual features from recent telemetry records.

    Returns a dict with keys used by the scoring model:
    - avg_recent_speed: mean speed from the last N telemetry points
    - fuel_level: most recent fuel reading
    - last_lat / last_lon: most recent known position
    """
    if not telemetry:
        return {
            "avg_recent_speed": 30.0,
            "fuel_level": 50.0,
            "last_lat": 0.0,
            "last_lon": 0.0,
        }

    speeds = [t.get("speed_kmh", 0.0) for t in telemetry]
    avg_speed = sum(speeds) / len(speeds) if speeds else 30.0

    latest = telemetry[0]
    return {
        "avg_recent_speed": round(avg_speed, 2),
        "fuel_level": latest.get("fuel_level", 50.0),
        "last_lat": latest.get("latitude", 0.0),
        "last_lon": latest.get("longitude", 0.0),
    }


def extract_route_features(candidate: Any, context: dict[str, Any]) -> dict[str, Any]:
    """Compute features for a single route candidate.

    Combines the route geometry with the telemetry context to produce
    model-ready features.
    """
    waypoints = candidate.waypoints
    total_distance = 0.0
    for i in range(len(waypoints) - 1):
        total_distance += _haversine_km(
            waypoints[i][0], waypoints[i][1],
            waypoints[i + 1][0], waypoints[i + 1][1],
        )

    if waypoints:
        start_lat, start_lon = waypoints[0]
        detour = _haversine_km(
            context["last_lat"], context["last_lon"],
            start_lat, start_lon,
        )
    else:
        detour = 0.0

    return {
        "normalized_distance": round(total_distance + detour, 4),
        "waypoint_count": len(waypoints),
        "avg_recent_speed": context["avg_recent_speed"],
        "fuel_level": context["fuel_level"],
        "detour_km": round(detour, 4),
    }


def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two GPS coordinates."""
    return haversine_m(lat1, lon1, lat2, lon2) / 1000
