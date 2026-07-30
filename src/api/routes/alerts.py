"""Maintenance alert rule management and alert feed endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Query, status

from src.api.alert_store import (
    acknowledge_alert,
    create_rule,
    delete_rule,
    get_rule,
    list_alerts,
    list_rules,
    set_rule_enabled,
)
from src.api.auth import get_current_operator
from src.api.models import AlertResponse, AlertRuleCreate, AlertRuleResponse
from src.ml.alert_engine import SUPPORTED_METRICS

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/alerts", tags=["alerts"])


@router.post("/rules", response_model=AlertRuleResponse)
def create_alert_rule(
    body: AlertRuleCreate,
    operator_id: str = Depends(get_current_operator),
) -> AlertRuleResponse:
    if body.metric not in SUPPORTED_METRICS:
        raise HTTPException(
            status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
            detail=f"Unsupported metric {body.metric!r}; supported: {sorted(SUPPORTED_METRICS)}",
        )
    row = create_rule(
        name=body.name,
        metric=body.metric,
        operator=body.operator.value,
        threshold=body.threshold,
        severity=body.severity.value,
        created_by=operator_id,
    )
    return AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])})


@router.get("/rules", response_model=list[AlertRuleResponse])
def get_alert_rules(
    enabled_only: bool = False,
    operator_id: str = Depends(get_current_operator),
) -> list[AlertRuleResponse]:
    rows = list_rules(enabled_only=enabled_only)
    return [AlertRuleResponse(**{**r, "enabled": bool(r["enabled"])}) for r in rows]


@router.patch("/rules/{rule_id}/enabled", response_model=AlertRuleResponse)
def toggle_alert_rule(
    rule_id: str,
    enabled: bool,
    operator_id: str = Depends(get_current_operator),
) -> AlertRuleResponse:
    if get_rule(rule_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    set_rule_enabled(rule_id, enabled)
    row = get_rule(rule_id)
    assert row is not None
    return AlertRuleResponse(**{**row, "enabled": bool(row["enabled"])})


@router.delete("/rules/{rule_id}")
def delete_alert_rule(
    rule_id: str,
    operator_id: str = Depends(get_current_operator),
) -> dict[str, str]:
    if get_rule(rule_id) is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Rule not found")
    delete_rule(rule_id)
    return {"status": "deleted", "id": rule_id}


@router.get("/", response_model=list[AlertResponse])
def get_alerts(
    vehicle_id: str | None = None,
    unacknowledged_only: bool = False,
    limit: int = Query(default=100, ge=1, le=500),
    operator_id: str = Depends(get_current_operator),
) -> list[AlertResponse]:
    rows = list_alerts(
        vehicle_id=vehicle_id,
        unacknowledged_only=unacknowledged_only,
        limit=limit,
    )
    return [AlertResponse(**{**r, "acknowledged": bool(r["acknowledged"])}) for r in rows]


@router.post("/{alert_id}/acknowledge", response_model=AlertResponse)
def acknowledge(
    alert_id: str,
    operator_id: str = Depends(get_current_operator),
) -> AlertResponse:
    row = acknowledge_alert(alert_id)
    if row is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Alert not found")
    logger.info("Alert %s acknowledged by %s", alert_id, operator_id)
    return AlertResponse(**{**row, "acknowledged": bool(row["acknowledged"])})
