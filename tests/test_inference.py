from __future__ import annotations

from src.api.models import RouteCandidate
from src.ml.features import extract_route_features, extract_telemetry_context
from src.ml.inference import score_route, score_routes_batch


def _make_candidate(
    route_id: str, waypoints: list[tuple[float, float]], distance_km: float,
) -> RouteCandidate:
    return RouteCandidate(route_id=route_id, waypoints=waypoints, distance_km=distance_km)


SAMPLE_TELEMETRY = [
    {"speed_kmh": 60.0, "fuel_level": 80.0, "latitude": 37.77, "longitude": -122.42},
    {"speed_kmh": 55.0, "fuel_level": 78.0, "latitude": 37.77, "longitude": -122.41},
]


def test_extract_telemetry_context_empty() -> None:
    ctx = extract_telemetry_context([])
    assert ctx["avg_recent_speed"] == 30.0
    assert ctx["fuel_level"] == 50.0


def test_extract_telemetry_context() -> None:
    ctx = extract_telemetry_context(SAMPLE_TELEMETRY)
    assert ctx["avg_recent_speed"] == 57.5
    assert ctx["fuel_level"] == 80.0


def test_extract_route_features() -> None:
    ctx = extract_telemetry_context(SAMPLE_TELEMETRY)
    candidate = _make_candidate("r1", [(37.77, -122.42), (37.78, -122.43)], 10.0)
    features = extract_route_features(candidate, ctx)
    assert "normalized_distance" in features
    assert features["waypoint_count"] == 2
    assert features["avg_recent_speed"] == 57.5


def test_score_route() -> None:
    candidate = _make_candidate("r1", [(37.77, -122.42), (37.78, -122.43)], 10.0)
    result = score_route(candidate, SAMPLE_TELEMETRY)
    assert result["route_id"] == "r1"
    assert result["score"] >= 0
    assert result["eta_minutes"] >= 0


def test_score_routes_batch() -> None:
    candidates = [
        _make_candidate("r1", [(37.77, -122.42), (37.78, -122.43)], 10.0),
        _make_candidate("r2", [(37.77, -122.42), (37.80, -122.45), (37.82, -122.47)], 20.0),
    ]
    results = score_routes_batch(candidates, SAMPLE_TELEMETRY)
    assert len(results) == 2
    assert results[0]["score"] >= results[1]["score"]


def test_score_routes_batch_empty() -> None:
    results = score_routes_batch([], SAMPLE_TELEMETRY)
    assert results == []
