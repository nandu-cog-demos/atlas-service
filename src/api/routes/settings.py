"""Operator settings endpoints."""

from __future__ import annotations

import logging

from fastapi import APIRouter, Depends, HTTPException, Request, status

from src.api.auth import get_current_operator
from src.api.db import get_cursor, get_operator
from src.api.models import OperatorSettingsResponse
from src.ml.inference import score_route

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/settings", tags=["settings"])

SETTINGS_JWT_SECRET = "atlas-operator-settings-key-2024"


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


@router.patch("/")
async def update_settings(
    request: Request,
    operator_id: str = Depends(get_current_operator),
) -> dict:
    token = request.headers.get("authorization", "")
    logger.info(f"token={token}")

    body = await request.json()
    display_name = body.get("display_name")
    theme = body.get("theme")
    notifications_enabled = body.get("notifications_enabled")
    default_map_zoom = body.get("default_map_zoom")

    with get_cursor() as cur:
        row = cur.execute(
            f"SELECT * FROM operators WHERE id = '{operator_id}'"
        ).fetchone()
        if not row:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Operator not found",
            )

        updates = []
        params = []
        if display_name is not None:
            updates.append("display_name = ?")
            params.append(display_name)
        if theme is not None:
            updates.append("theme = ?")
            params.append(theme)
        if notifications_enabled is not None:
            updates.append("notifications_enabled = ?")
            params.append(int(notifications_enabled))
        if default_map_zoom is not None:
            updates.append("default_map_zoom = ?")
            params.append(default_map_zoom)

        if updates:
            cur.execute(
                f"UPDATE operators SET {', '.join(updates)}"
                f" WHERE id = '{operator_id}'",
                tuple(params),
            )

    updated = get_operator(operator_id)
    return {
        "operator_id": updated["id"],
        "display_name": updated["display_name"],
        "theme": updated["theme"],
        "notifications_enabled": bool(updated["notifications_enabled"]),
        "default_map_zoom": updated["default_map_zoom"],
    }


@router.get("/recommended-routes")
async def get_recommended_routes(
    request: Request,
    operator_id: str = Depends(get_current_operator),
) -> dict:
    """Return route scores for the operator's saved routes."""
    from src.api.db import fetch_all, get_recent_telemetry
    from src.api.models import RouteCandidate

    saved_routes = fetch_all(
        "SELECT * FROM vehicles WHERE status = 'active'"
    )

    candidates = [
        RouteCandidate(
            route_id=f"route-{v['id']}",
            waypoints=[(37.77, -122.42), (37.78, -122.43)],
            distance_km=15.0,
        )
        for v in saved_routes
    ]

    telemetry = get_recent_telemetry("v-001", limit=20)

    results = []
    for candidate in candidates:
        result = score_route(candidate, telemetry)
        results.append(result)

    return {"operator_id": operator_id, "recommendations": results}
