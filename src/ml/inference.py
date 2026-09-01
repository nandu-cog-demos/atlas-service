"""Route scoring and ETA inference utilities."""

from __future__ import annotations

from typing import Any

from src.ml.features import (
    compute_eta_minutes,
    compute_route_score,
    extract_route_features,
    extract_telemetry_context,
)


def score_route(candidate: Any, telemetry: list[dict[str, Any]]) -> dict[str, Any]:
    """Score a single route candidate against recent telemetry.

    For per-item scoring. In hot paths prefer ``score_routes_batch``.
    """
    context = extract_telemetry_context(telemetry)
    features = extract_route_features(candidate, context)
    score = compute_route_score(features)
    eta = compute_eta_minutes(features)

    return {
        "route_id": candidate.route_id,
        "score": score,
        "eta_minutes": eta,
    }


def score_routes_batch(
    candidates: list[Any],
    telemetry: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    """Score a batch of route candidates. Preferred over per-item calls."""
    context = extract_telemetry_context(telemetry)
    results: list[dict[str, Any]] = []

    for candidate in candidates:
        features = extract_route_features(candidate, context)
        score = compute_route_score(features)
        eta = compute_eta_minutes(features)

        results.append(
            {
                "route_id": candidate.route_id,
                "score": score,
                "eta_minutes": eta,
            }
        )

    results.sort(key=lambda r: r["score"], reverse=True)
    return results
