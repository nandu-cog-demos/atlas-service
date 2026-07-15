"""Alert listing and acknowledgement endpoints."""

from __future__ import annotations

from typing import Any

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.auth import get_current_operator
from src.api.db import acknowledge_alert, list_alerts
from src.api.models import AlertResponse

router = APIRouter(prefix="/alerts", tags=["alerts"])


def _to_response(row: dict[str, Any]) -> AlertResponse:
    return AlertResponse(
        id=row["id"],
        zone_event_id=row["zone_event_id"],
        vehicle_id=row["vehicle_id"],
        zone_id=row["zone_id"],
        created_at=row["created_at"],
        acknowledged=bool(row["acknowledged"]),
        acknowledged_by=row["acknowledged_by"],
        acknowledged_at=row["acknowledged_at"],
    )


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    acknowledged: bool | None = Query(default=None),
    limit: int = Query(default=50, ge=1),
    operator_id: str = Depends(get_current_operator),
) -> list[AlertResponse]:
    rows = list_alerts(acknowledged=acknowledged, limit=limit)
    return [_to_response(row) for row in rows]


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge_alert_endpoint(
    alert_id: str,
    operator_id: str = Depends(get_current_operator),
) -> AlertResponse:
    row = acknowledge_alert(alert_id, operator_id)
    if row is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Alert not found",
        )
    return _to_response(row)
