"""Route scoring endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from src.api.auth import get_current_operator
from src.api.db import get_recent_telemetry
from src.api.models import RouteScoreRequest, RouteScoreResponse, RouteScoreResult
from src.ml.inference import score_routes_batch

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/routes", tags=["routes"])


@router.post("/score", response_model=RouteScoreResponse)
def score_routes(
    request: RouteScoreRequest,
    operator_id: str = Depends(get_current_operator),
) -> RouteScoreResponse:
    telemetry = get_recent_telemetry(request.vehicle_id, limit=20)
    results = score_routes_batch(request.candidates, telemetry)
    return RouteScoreResponse(
        vehicle_id=request.vehicle_id,
        results=[
            RouteScoreResult(
                route_id=r["route_id"],
                score=r["score"],
                eta_minutes=r["eta_minutes"],
            )
            for r in results
        ],
    )
