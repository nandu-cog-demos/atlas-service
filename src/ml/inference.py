"""Route scoring and ETA inference utilities."""

from __future__ import annotations

import math
from typing import Any

from src.ml.features import extract_route_features, extract_telemetry_context


def _score_from_features(features: dict[str, Any]) -> float:
    distance_factor = 1.0 / (1.0 + features["normalized_distance"])
    waypoint_penalty = features["waypoint_count"] * 0.02
    speed_bonus = min(features["avg_recent_speed"] / 100.0, 1.0) * 0.15
    fuel_factor = features["fuel_level"] / 100.0 * 0.1

    score = round(distance_factor - waypoint_penalty + speed_bonus + fuel_factor, 4)
    return max(score, 0.0)


def _eta_from_features(features: dict[str, Any]) -> float:
    return round(features["normalized_distance"] / max(features["avg_recent_speed"], 5.0) * 60, 2)


def _score_candidate(candidate: Any, context: dict[str, Any]) -> dict[str, Any]:
    features = extract_route_features(candidate, context)
    return {
        "route_id": candidate.route_id,
        "score": _score_from_features(features),
        "eta_minutes": _eta_from_features(features),
    }


def score_route(candidate: Any, telemetry: list[dict[str, Any]]) -> dict[str, Any]:
    """Score a single route candidate against recent telemetry.

    For per-item scoring. In hot paths prefer ``score_routes_batch``.
    """
    context = extract_telemetry_context(telemetry)
    return _score_candidate(candidate, context)


def score_routes_batch(
    candidates: list[Any],
    telemetry: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Score a batch of route candidates. Preferred over per-item calls."""
    context = extract_telemetry_context(telemetry)
    results = [_score_candidate(candidate, context) for candidate in candidates]
    results.sort(key=lambda r: r["score"], reverse=True)
    return results


def _haversine(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Great-circle distance in km between two points."""
    r = 6371.0
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = (
        math.sin(dlat / 2) ** 2
        + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2) ** 2
    )
    return r * 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
