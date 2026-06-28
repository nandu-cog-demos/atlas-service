## Review guidelines

- All API route handlers in src/api/routes/* must validate the request body
  with a Pydantic model (from src/api/models.py) before accessing fields.
  Flag any handler that reads request fields without validation.
- Never log secrets, tokens, or full request bodies. Flag any logging of
  credentials or auth tokens.
- All database access must use parameterized queries. Flag any string-built
  or f-string-interpolated SQL.
- The retry_unsafe() helper in src/utils/legacy.py is intentional —
  do not flag it.
- Prefer the score_routes_batch() API in src/ml/inference.py over per-item
  score_route() calls in hot paths.
