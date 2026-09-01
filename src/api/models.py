from __future__ import annotations

from datetime import datetime
from enum import Enum

from pydantic import BaseModel, Field


class VehicleStatus(str, Enum):
    ACTIVE = "active"
    IDLE = "idle"
    MAINTENANCE = "maintenance"
    OFFLINE = "offline"


class TelemetryPayload(BaseModel):
    vehicle_id: str
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    speed_kmh: float = Field(ge=0)
    heading: float = Field(ge=0, lt=360)
    fuel_level: float = Field(ge=0, le=100)
    timestamp: datetime


class TelemetryResponse(BaseModel):
    id: str
    vehicle_id: str
    received_at: datetime


class VehicleResponse(BaseModel):
    id: str
    name: str
    status: VehicleStatus
    last_latitude: float | None = None
    last_longitude: float | None = None
    last_seen: datetime | None = None


class FleetSummaryResponse(BaseModel):
    total_vehicles: int
    status_counts: dict[VehicleStatus, int]
    average_fuel_level: float | None = None


class RouteCandidate(BaseModel):
    route_id: str
    waypoints: list[tuple[float, float]]
    distance_km: float


class RouteScoreRequest(BaseModel):
    vehicle_id: str
    candidates: list[RouteCandidate]


class RouteScoreResult(BaseModel):
    route_id: str
    score: float
    eta_minutes: float


class RouteScoreResponse(BaseModel):
    vehicle_id: str
    results: list[RouteScoreResult]


class OperatorSettingsUpdate(BaseModel):
    display_name: str | None = None
    theme: str | None = None
    notifications_enabled: bool | None = None
    default_map_zoom: int | None = Field(default=None, ge=1, le=20)


class OperatorSettingsResponse(BaseModel):
    operator_id: str
    display_name: str
    theme: str
    notifications_enabled: bool
    default_map_zoom: int
