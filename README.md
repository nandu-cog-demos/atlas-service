# Atlas Service

Atlas is a fleet telemetry and route-optimization service. It ingests
real-time location and sensor data from connected vehicles, stores it,
and serves ETA predictions and route scores to operators through a REST
API and a web dashboard.

## Features

- **Telemetry ingestion** — high-throughput endpoint for GPS + sensor
  payloads from fleet devices.
- **Route scoring** — a hard-coded heuristic (distance, waypoint count,
  recent speed, fuel level) that ranks candidate routes and predicts ETAs
  from recent telemetry. There is no trained model or model artifact.
- **Operator dashboard** — a React/TypeScript UI for monitoring live fleet
  status, vehicle detail, and route recommendations.
- **Token-based auth** — JWT bearer tokens are validated on protected
  endpoints. There is no login or token-issuance endpoint: tokens must be
  minted out of band with `src.api.auth.create_token`.

## Architecture

- `src/api` — FastAPI application: route handlers, auth, and data access.
  Storage is an in-memory SQLite database created at process start
  (`src/api/db.py`); all data is lost when the process exits, and there is
  no external database or migration step.
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

The only environment variable the code reads is:

- `JWT_SECRET` — signing secret for operator tokens (`src/api/auth.py`).
  Defaults to an insecure development value if unset.

## Testing

```bash
pytest                 # backend
cd web && npm test     # frontend
```

## License

MIT
