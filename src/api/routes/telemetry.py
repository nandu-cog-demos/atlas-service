"""Telemetry ingestion endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from src.api.auth import get_current_operator
from src.api.db import insert_telemetry
from src.api.models import TelemetryPayload, TelemetryResponse

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/telemetry", tags=["telemetry"])


@router.post("/", response_model=TelemetryResponse)
def ingest_telemetry(
    payload: TelemetryPayload,
    operator_id: str = Depends(get_current_operator),
) -> TelemetryResponse:
    logger.info("Telemetry received for vehicle %s", payload.vehicle_id)
    record_id = insert_telemetry(
        vehicle_id=payload.vehicle_id,
        latitude=payload.latitude,
        longitude=payload.longitude,
        speed_kmh=payload.speed_kmh,
        heading=payload.heading,
        fuel_level=payload.fuel_level,
        timestamp=payload.timestamp,
    )
    return TelemetryResponse(
        id=record_id,
        vehicle_id=payload.vehicle_id,
        received_at=datetime.now(timezone.utc),
    )
