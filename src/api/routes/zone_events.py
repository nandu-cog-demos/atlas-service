"""Zone event endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, Query

from src.api.auth import get_current_operator
from src.api.db import list_zone_events
from src.api.models import ZoneEventResponse

router = APIRouter(prefix="/zone-events", tags=["zone-events"])


def _to_response(row: dict[str, Any]) -> ZoneEventResponse:
    return ZoneEventResponse(
        id=row["id"],
        vehicle_id=row["vehicle_id"],
        zone_id=row["zone_id"],
        event_type=row["event_type"],
        latitude=row["latitude"],
        longitude=row["longitude"],
        occurred_at=row["occurred_at"],
    )


@router.get("/", response_model=list[ZoneEventResponse])
def get_zone_events(
    vehicle_id: str | None = Query(default=None),
    zone_id: str | None = Query(default=None),
    limit: int = Query(default=50, ge=1),
    operator_id: str = Depends(get_current_operator),
) -> list[ZoneEventResponse]:
    rows = list_zone_events(vehicle_id=vehicle_id, zone_id=zone_id, limit=limit)
    return [_to_response(row) for row in rows]
