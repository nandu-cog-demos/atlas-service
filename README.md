# Atlas Service

Atlas is a fleet telemetry and route-optimization service. It ingests
real-time location and sensor data from connected vehicles, persists it,
and serves ETA predictions and route scores to operators through a REST
API and a web dashboard.

## Features

- **Telemetry ingestion** — high-throughput endpoint for GPS + sensor
  payloads from fleet devices, plus a batch endpoint
  (`POST /api/v1/telemetry/batch`) for buffered uploads.
- **Fleet summary** — `GET /api/v1/vehicles/summary` returns counts by
  status, average fuel/speed from latest telemetry, and stale-vehicle counts.
- **Vehicle management** — filter vehicles by status
  (`GET /api/v1/vehicles/?status=idle`) and update operational status
  (`PATCH /api/v1/vehicles/{id}/status`).
- **Route scoring** — a lightweight inference module that ranks candidate
  routes and predicts ETAs from recent telemetry.
- **Operator dashboard** — a React/TypeScript UI for monitoring live fleet
  status, vehicle detail, and route recommendations.
- **Token-based auth** — session/token handling for operators and devices.

## Architecture

- `src/api` — FastAPI application: route handlers, auth, and database access.
- `src/ml` — route-scoring and ETA inference utilities.
- `web` — React + TypeScript operator dashboard.
- `tests` — unit and integration tests.

## Getting started

```bash
# Backend
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn src.api.main:app --reload

# Frontend
cd web && npm install && npm run dev
```

## Configuration

Copy `.env.example` to `.env` and set:

- `DATABASE_URL` — Postgres connection string
- `JWT_SECRET` — signing secret for operator tokens
- `MODEL_PATH` — path to the route-scoring model artifact

## Testing

```bash
pytest                 # backend
cd web && npm test     # frontend
```

## License

MIT
