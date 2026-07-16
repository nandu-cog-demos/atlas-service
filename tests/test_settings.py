from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.db import update_operator


def test_get_settings(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/settings/", headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["operator_id"] == "op-001"


def test_update_settings_valid_theme(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch("/api/v1/settings/", json={"theme": "dark"}, headers=auth_headers)
    assert resp.status_code == 200
    assert resp.json()["theme"] == "dark"


def test_update_settings_invalid_theme(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch("/api/v1/settings/", json={"theme": "blursed-mode"}, headers=auth_headers)
    assert resp.status_code == 422


def test_update_operator_rejects_unknown_columns() -> None:
    with pytest.raises(ValueError, match="Unknown operator columns"):
        update_operator("op-001", {"theme = 'x' WHERE 1=1; --": "y"})
