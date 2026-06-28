"""Feature extraction and scoring helpers for route optimization.

This module consolidates all feature-engineering and scoring logic used by
the inference layer.  Keeping extraction and scoring co-located makes the
pipeline easier to test and evolve independently of the inference API.
"""

from __future__ import annotations

import math
from typing import Any

# ---------------------------------------------------------------------------
# Telemetry context
# ---------------------------------------------------------------------------

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


# ---------------------------------------------------------------------------
# Route feature extraction
# ---------------------------------------------------------------------------

def extract_route_features(candidate: Any, context: dict[str, Any]) -> dict[str, Any]:
    """Compute features for a single route candidate.

    Combines the route geometry with the telemetry context to produce
    model-ready features.
    """
    waypoints = candidate.waypoints
    total_distance = _sum_segment_distances(waypoints)

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


def _sum_segment_distances(waypoints: list[tuple[float, float]]) -> float:
    """Sum haversine distances between consecutive waypoints."""
    total = 0.0
    for i in range(len(waypoints) - 1):
        total += _haversine_km(
            waypoints[i][0], waypoints[i][1],
            waypoints[i + 1][0], waypoints[i + 1][1],
        )
    return total


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------

def compute_route_score(features: dict[str, Any]) -> float:
    """Return a composite route score in [0, 1].

    The score combines distance efficiency, waypoint complexity, recent
    vehicle speed, and fuel state.
    """
    distance_factor = 1.0 / (1.0 + features["normalized_distance"])
    waypoint_penalty = features["waypoint_count"] * 0.02
    speed_bonus = min(features["avg_recent_speed"] / 100.0, 1.0) * 0.15
    fuel_factor = features["fuel_level"] / 100.0 * 0.1

    score = round(distance_factor - waypoint_penalty + speed_bonus + fuel_factor, 4)
    return max(score, 0.0)


def compute_eta_minutes(features: dict[str, Any]) -> float:
    """Estimate arrival time in minutes from route features."""
    speed = max(features["avg_recent_speed"], 5.0)
    return round(features["normalized_distance"] / speed * 60, 2)


# ---------------------------------------------------------------------------
# Geo helpers
# ---------------------------------------------------------------------------

def _haversine_km(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two GPS coordinates."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1))
        * math.cos(math.radians(lat2))
        * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
