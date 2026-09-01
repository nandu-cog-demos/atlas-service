from __future__ import annotations

from fastapi.testclient import TestClient

from src.api.main import app


def test_health(client: TestClient) -> None:
    resp = client.get("/health")
    assert resp.status_code == 200
    assert resp.json() == {"status": "ok", "version": app.version}
