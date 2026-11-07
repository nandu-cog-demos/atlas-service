"""Vehicle list and detail endpoints."""

from __future__ import annotations

import logging
import os
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import get_current_operator
from src.api.db import get_recent_telemetry, get_vehicle, list_vehicles
from src.api.models import VehicleResponse, VehicleStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])

LOW_FUEL_THRESHOLD_PCT = float(os.getenv("LOW_FUEL_THRESHOLD_PCT", "15"))


def _to_response(row: dict[str, Any]) -> VehicleResponse:
    fuel_level = row["fuel_level"]
    return VehicleResponse(
        id=row["id"],
        name=row["name"],
        status=VehicleStatus(row["status"]),
        last_latitude=row["last_latitude"],
        last_longitude=row["last_longitude"],
        last_seen=row["last_seen"],
        fuel_level=fuel_level,
        low_fuel=fuel_level is not None and fuel_level < LOW_FUEL_THRESHOLD_PCT,
    )


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    operator_id: str = Depends(get_current_operator),
) -> list[VehicleResponse]:
    return [_to_response(r) for r in list_vehicles()]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_detail(
    vehicle_id: str,
    operator_id: str = Depends(get_current_operator),
) -> VehicleResponse:
    row = get_vehicle(vehicle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return _to_response(row)


@router.get("/{vehicle_id}/telemetry")
def get_vehicle_telemetry(
    vehicle_id: str,
    limit: int = 50,
    operator_id: str = Depends(get_current_operator),
) -> list[dict]:
    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return get_recent_telemetry(vehicle_id, limit=limit)
