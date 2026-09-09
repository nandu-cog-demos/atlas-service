"""Telemetry ingestion endpoints."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

from fastapi import APIRouter, Depends

from src.api.auth import get_current_operator
from src.api.db import get_vehicle, insert_telemetry
from src.api.models import (
    TelemetryBatchRequest,
    TelemetryBatchResponse,
    TelemetryPayload,
    TelemetryResponse,
)

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


@router.post("/batch", response_model=TelemetryBatchResponse)
def ingest_telemetry_batch(
    body: TelemetryBatchRequest,
    operator_id: str = Depends(get_current_operator),
) -> TelemetryBatchResponse:
    known: dict[str, bool] = {}
    accepted = 0
    rejected: list[str] = []
    for record in body.records:
        if record.vehicle_id not in known:
            known[record.vehicle_id] = get_vehicle(record.vehicle_id) is not None
        if not known[record.vehicle_id]:
            rejected.append(record.vehicle_id)
            continue
        insert_telemetry(
            vehicle_id=record.vehicle_id,
            latitude=record.latitude,
            longitude=record.longitude,
            speed_kmh=record.speed_kmh,
            heading=record.heading,
            fuel_level=record.fuel_level,
            timestamp=record.timestamp,
        )
        accepted += 1
    logger.info("Telemetry batch: %d accepted, %d rejected", accepted, len(rejected))
    return TelemetryBatchResponse(
        accepted=accepted,
        rejected=len(rejected),
        rejected_vehicle_ids=sorted(set(rejected)),
        received_at=datetime.now(timezone.utc),
    )
