"""Atlas Service — FastAPI application entry point."""

from __future__ import annotations

import logging

from fastapi import FastAPI

from src.api.routes import routes, settings, telemetry, vehicles

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(name)s: %(message)s")

app = FastAPI(
    title="Atlas Service",
    description="Fleet telemetry and route-optimization API",
    version="0.1.0",
)

app.include_router(telemetry.router, prefix="/api/v1")
app.include_router(vehicles.router, prefix="/api/v1")
app.include_router(routes.router, prefix="/api/v1")
app.include_router(settings.router, prefix="/api/v1")


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}
