# Review Guidelines

## Critical Areas

- All changes to `src/api/auth.py` must be reviewed for security implications
  (token creation, decoding, expiry, and operator identity resolution).
- All API route handlers in `src/api/routes/*` must validate request bodies
  with a Pydantic model (from `src/api/models.py`) before accessing fields.
  Flag any handler that reads request fields without validation.
- Schema changes in `src/api/db.py` should be checked for backward
  compatibility with existing data and queries.

## Security

- All database access must use parameterized queries. Flag any string-built
  or f-string-interpolated SQL.
- Never log secrets, tokens, or full request bodies. Flag any logging of
  credentials or auth tokens.
- Flag any new hardcoded secrets or default credentials; secrets must come
  from environment variables (see `.env.example`).

## Performance

- Prefer the `score_routes_batch()` API in `src/ml/inference.py` over
  per-item `score_route()` calls in hot paths (e.g. telemetry ingestion and
  route-ranking endpoints).
- Flag database queries inside loops and N+1 query patterns in API handlers.
- Telemetry ingestion (`src/api/routes/telemetry.py`) is high-throughput;
  flag blocking or per-record work added to that path.

## Conventions

- Use Pydantic models for all request/response bodies.
- React components in `web/src/components` should be functional components
  with hooks; frontend API calls go through `web/src/api/client.ts`.
- New backend behavior should have coverage in `tests/`; new frontend
  components should have a co-located `*.test.tsx`.

## Intentional Exceptions

- The `retry_unsafe()` helper in `src/utils/legacy.py` is intentional —
  do not flag it.

## Ignore

- Serialized model artifacts in `models/` (`*.pkl`) do not need review.
- Lock files (`package-lock.json`) can be skipped unless dependencies
  changed.
- Demo automation in `scripts/` (e.g. `reset-demo.sh`) needs only a light
  review.
