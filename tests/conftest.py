from __future__ import annotations

import os

os.environ.setdefault("JWT_SECRET", "test-secret")

import pytest  # noqa: E402
from fastapi.testclient import TestClient  # noqa: E402

from src.api.auth import create_token  # noqa: E402
from src.api.main import app  # noqa: E402


@pytest.fixture()
def client() -> TestClient:
    return TestClient(app)


@pytest.fixture()
def auth_headers() -> dict[str, str]:
    token = create_token("op-001")
    return {"Authorization": f"Bearer {token}"}
