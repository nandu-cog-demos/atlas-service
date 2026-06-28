"""Operator settings endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from src.api.auth import get_current_operator
from src.api.db import get_operator, update_operator
from src.api.models import OperatorSettingsResponse, OperatorSettingsUpdate

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])


@router.get("/", response_model=OperatorSettingsResponse)
def get_settings(
    operator_id: str = Depends(get_current_operator),
) -> OperatorSettingsResponse:
    row = get_operator(operator_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")
    return OperatorSettingsResponse(
        operator_id=row["id"],
        display_name=row["display_name"],
        theme=row["theme"],
        notifications_enabled=bool(row["notifications_enabled"]),
        default_map_zoom=row["default_map_zoom"],
    )


@router.patch("/", response_model=OperatorSettingsResponse)
def update_settings(
    body: OperatorSettingsUpdate,
    operator_id: str = Depends(get_current_operator),
) -> OperatorSettingsResponse:
    row = get_operator(operator_id)
    if not row:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Operator not found")

    updates = body.model_dump(exclude_unset=True)
    if updates:
        update_operator(operator_id, updates)

    updated = get_operator(operator_id)
    return OperatorSettingsResponse(
        operator_id=updated["id"],
        display_name=updated["display_name"],
        theme=updated["theme"],
        notifications_enabled=bool(updated["notifications_enabled"]),
        default_map_zoom=updated["default_map_zoom"],
    )
