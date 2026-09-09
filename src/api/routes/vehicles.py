"""Vehicle list, detail, status, and fleet summary endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timedelta, timezone
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.auth import get_current_operator
from src.api.db import (
    count_vehicles_by_status,
    get_latest_telemetry_per_vehicle,
    get_recent_telemetry,
    get_vehicle,
    list_vehicles,
    update_vehicle_status,
)
from src.api.models import (
    FleetSummaryResponse,
    VehicleResponse,
    VehicleStatus,
    VehicleStatusUpdate,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/vehicles", tags=["vehicles"])


def _to_response(row: dict[str, Any]) -> VehicleResponse:
    return VehicleResponse(
        id=row["id"],
        name=row["name"],
        status=VehicleStatus(row["status"]),
        last_latitude=row["last_latitude"],
        last_longitude=row["last_longitude"],
        last_seen=row["last_seen"],
    )


def _parse_ts(value: str) -> datetime:
    ts = datetime.fromisoformat(value.replace("Z", "+00:00"))
    return ts if ts.tzinfo else ts.replace(tzinfo=timezone.utc)


@router.get("/", response_model=list[VehicleResponse])
def get_vehicles(
    status_filter: VehicleStatus | None = Query(default=None, alias="status"),
    operator_id: str = Depends(get_current_operator),
) -> list[VehicleResponse]:
    rows = list_vehicles(status_filter.value if status_filter else None)
    return [_to_response(r) for r in rows]


@router.get("/summary", response_model=FleetSummaryResponse)
def get_fleet_summary(
    stale_after_minutes: int = Query(default=30, ge=1),
    operator_id: str = Depends(get_current_operator),
) -> FleetSummaryResponse:
    counts = count_vehicles_by_status()
    by_status = {s: counts.get(s.value, 0) for s in VehicleStatus}

    latest = get_latest_telemetry_per_vehicle()
    fuel = [r["fuel_level"] for r in latest]
    speed = [r["speed_kmh"] for r in latest]

    cutoff = datetime.now(timezone.utc) - timedelta(minutes=stale_after_minutes)
    stale = 0
    for v in list_vehicles():
        if v["status"] in (VehicleStatus.MAINTENANCE.value, VehicleStatus.OFFLINE.value):
            continue
        if v["last_seen"] is None or _parse_ts(v["last_seen"]) < cutoff:
            stale += 1

    return FleetSummaryResponse(
        total_vehicles=sum(by_status.values()),
        by_status=by_status,
        average_fuel_level=round(sum(fuel) / len(fuel), 2) if fuel else None,
        average_speed_kmh=round(sum(speed) / len(speed), 2) if speed else None,
        stale_vehicles=stale,
        stale_threshold_minutes=stale_after_minutes,
    )


@router.get("/{vehicle_id}", response_model=VehicleResponse)
def get_vehicle_detail(
    vehicle_id: str,
    operator_id: str = Depends(get_current_operator),
) -> VehicleResponse:
    row = get_vehicle(vehicle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return _to_response(row)


@router.patch("/{vehicle_id}/status", response_model=VehicleResponse)
def set_vehicle_status(
    vehicle_id: str,
    body: VehicleStatusUpdate,
    operator_id: str = Depends(get_current_operator),
) -> VehicleResponse:
    row = get_vehicle(vehicle_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    logger.info(
        "Operator %s set vehicle %s status %s -> %s",
        operator_id, vehicle_id, row["status"], body.status.value,
    )
    update_vehicle_status(vehicle_id, body.status.value)
    return _to_response(get_vehicle(vehicle_id))


@router.get("/{vehicle_id}/telemetry")
def get_vehicle_telemetry(
    vehicle_id: str,
    limit: int = Query(default=50, ge=1, le=1000),
    operator_id: str = Depends(get_current_operator),
) -> list[dict]:
    vehicle = get_vehicle(vehicle_id)
    if not vehicle:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Vehicle not found")
    return get_recent_telemetry(vehicle_id, limit=limit)
