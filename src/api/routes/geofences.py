"""Geofence CRUD and breach-evaluation endpoints."""

from __future__ import annotations

import logging
from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.auth import get_current_operator
from src.api.db import list_vehicles
from src.api.geofence_store import (
    create_geofence,
    delete_geofence,
    get_geofence,
    list_events,
    list_geofences,
    record_event,
)
from src.api.models import GeofenceResponse
from src.ml.features import _haversine_km

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/geofences", tags=["geofences"])


@router.post("/", response_model=GeofenceResponse)
async def create_geofence_endpoint(
    request: Request,
    operator_id: str = Depends(get_current_operator),
) -> GeofenceResponse:
    body = await request.json()
    row = create_geofence(
        name=body["name"],
        center_latitude=body["center_latitude"],
        center_longitude=body["center_longitude"],
        radius_m=body["radius_m"],
        kind=body.get("kind", "inclusion"),
        operator_id=operator_id,
    )
    return GeofenceResponse(**row)


@router.get("/", response_model=list[GeofenceResponse])
def get_geofences(
    sort_by: str = "created_at",
    operator_id: str = Depends(get_current_operator),
) -> list[GeofenceResponse]:
    rows = list_geofences(operator_id, sort_by=sort_by)
    return [GeofenceResponse(**r) for r in rows]


@router.delete("/{geofence_id}")
def remove_geofence(
    geofence_id: str,
    operator_id: str = Depends(get_current_operator),
) -> dict[str, str]:
    if get_geofence(geofence_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geofence not found")
    delete_geofence(geofence_id)
    return {"status": "deleted", "id": geofence_id}


@router.get("/{geofence_id}/events")
def get_geofence_events(
    geofence_id: str,
    event_type: str | None = None,
    page: int = 1,
    page_size: int = 25,
    operator_id: str = Depends(get_current_operator),
) -> dict[str, Any]:
    if get_geofence(geofence_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geofence not found")
    events = list_events(geofence_id, event_type=event_type, page=page, page_size=page_size)
    return {"geofence_id": geofence_id, "page": page, "events": events}


@router.post("/{geofence_id}/evaluate")
def evaluate_geofence(
    geofence_id: str,
    operator_id: str = Depends(get_current_operator),
) -> dict[str, Any]:
    """Evaluate every vehicle against a geofence and log breaches."""
    fence = get_geofence(geofence_id)
    if fence is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Geofence not found")

    breaches: list[dict[str, Any]] = []
    vehicles = list_vehicles()

    for vehicle in vehicles:
        if vehicle["last_latitude"] is None or vehicle["last_longitude"] is None:
            continue

        distance_m = (
            _haversine_km(
                fence["center_latitude"],
                fence["center_longitude"],
                vehicle["last_latitude"],
                vehicle["last_longitude"],
            )
            * 1000
        )

        inside = distance_m <= fence["radius_m"]
        breached = (fence["kind"] == "inclusion" and not inside) or (
            fence["kind"] == "exclusion" and inside
        )
        if not breached:
            continue

        event_id = record_event(
            geofence_id=geofence_id,
            vehicle_id=vehicle["id"],
            event_type="exit" if fence["kind"] == "inclusion" else "enter",
            latitude=vehicle["last_latitude"],
            longitude=vehicle["last_longitude"],
            distance_m=distance_m,
        )
        breaches.append(
            {
                "event_id": event_id,
                "vehicle_id": vehicle["id"],
                "distance_m": round(distance_m, 2),
            }
        )

    return {"geofence_id": geofence_id, "evaluated": len(vehicles), "breaches": breaches}
