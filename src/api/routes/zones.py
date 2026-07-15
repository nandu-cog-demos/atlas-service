"""Geofence zone endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.auth import get_current_operator
from src.api.db import create_zone, deactivate_zone, list_zones
from src.api.geofence import invalidate_active_zones_cache
from src.api.models import ZoneCreate, ZoneResponse

router = APIRouter(prefix="/zones", tags=["zones"])


def _to_response(row: dict[str, Any]) -> ZoneResponse:
    return ZoneResponse(
        id=row["id"],
        name=row["name"],
        center_latitude=row["center_latitude"],
        center_longitude=row["center_longitude"],
        radius_m=row["radius_m"],
        zone_type=row["zone_type"],
        active=bool(row["active"]),
        created_at=row["created_at"],
    )


@router.post("/", response_model=ZoneResponse)
def create_geofence_zone(
    body: ZoneCreate,
    operator_id: str = Depends(get_current_operator),
) -> ZoneResponse:
    row = create_zone(
        name=body.name,
        center_latitude=body.center_latitude,
        center_longitude=body.center_longitude,
        radius_m=body.radius_m,
        zone_type=body.zone_type,
    )
    invalidate_active_zones_cache()
    return _to_response(row)


@router.get("/", response_model=list[ZoneResponse])
def get_zones(
    active: bool | None = Query(default=None),
    operator_id: str = Depends(get_current_operator),
) -> list[ZoneResponse]:
    return [_to_response(row) for row in list_zones(active=active)]


@router.delete("/{zone_id}", response_model=ZoneResponse)
def deactivate_geofence_zone(
    zone_id: str,
    operator_id: str = Depends(get_current_operator),
) -> ZoneResponse:
    row = deactivate_zone(zone_id)
    if not row:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Zone not found",
        )
    invalidate_active_zones_cache()
    return _to_response(row)
