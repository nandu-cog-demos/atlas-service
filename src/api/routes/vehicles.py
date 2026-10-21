"""Vehicle list and detail endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.auth import get_current_operator
from src.api.db import get_recent_telemetry, get_vehicle, list_vehicles
from src.api.models import VehicleResponse, VehicleStatus

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    operator_id: str = Depends(get_current_operator),
) -> list[VehicleResponse]:
    rows = list_vehicles()
    return [
        VehicleResponse(
            id=r["id"],
            name=r["name"],
            status=VehicleStatus(r["status"]),
            last_latitude=r["last_latitude"],
            last_longitude=r["last_longitude"],
            last_seen=r["last_seen"],
        )
        for r in rows
    ]


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_detail(
    vehicle_id: str,
    operator_id: str = Depends(get_current_operator),
) -> VehicleResponse:
    row = get_vehicle(vehicle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return VehicleResponse(
        id=row["id"],
        name=row["name"],
        status=VehicleStatus(row["status"]),
        last_latitude=row["last_latitude"],
        last_longitude=row["last_longitude"],
        last_seen=row["last_seen"],
    )


@router.get("/{vehicle_id}/telemetry")
def get_vehicle_telemetry(
    vehicle_id: str,
    limit: int = Query(50, ge=1, le=500),
    operator_id: str = Depends(get_current_operator),
) -> list[dict]:
    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return get_recent_telemetry(vehicle_id, limit=limit)
