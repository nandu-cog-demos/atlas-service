from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.auth import create_token
from src.api.main import app


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    token = create_token("op-001")
    return {"Authorization": f"Bearer {token}"}
