"""Fleet-wide summary endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends

from src.api.auth import get_current_operator
from src.api.db import get_fleet_average_fuel_level, get_fleet_status_counts
from src.api.models import FleetSummaryResponse, VehicleStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/fleet", tags=["fleet"])


@router.get("/summary", response_model=FleetSummaryResponse)
def get_fleet_summary(
    operator_id: str = Depends(get_current_operator),
) -> FleetSummaryResponse:
    counts = get_fleet_status_counts()
    status_counts = {s.value: counts.get(s.value, 0) for s in VehicleStatus}
    return FleetSummaryResponse(
        total_vehicles=sum(counts.values()),
        status_counts=status_counts,
        average_fuel_level=get_fleet_average_fuel_level(),
    )
