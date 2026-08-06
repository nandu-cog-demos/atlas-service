from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.db import get_operator, update_operator


def test_get_settings(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.get("/api/v1/settings/", headers=auth_headers)
    assert resp.status_code == 200
    data = resp.json()
    assert data["operator_id"] == "op-001"
    assert data["theme"] in {"light", "dark", "system"}


def test_update_settings_valid_theme(client: TestClient, auth_headers: dict[str, str]) -> None:
    resp = client.patch("/api/v1/settings/", headers=auth_headers, json={"theme": "dark"})
    assert resp.status_code == 200
    assert resp.json()["theme"] == "dark"


def test_update_settings_rejects_invalid_theme(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.patch(
        "/api/v1/settings/", headers=auth_headers, json={"theme": "blursed-mode"}
    )
    assert resp.status_code == 422
    assert get_operator("op-001")["theme"] != "blursed-mode"


def test_update_settings_multiple_fields(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.patch(
        "/api/v1/settings/",
        headers=auth_headers,
        json={"display_name": "Ops Lead", "notifications_enabled": False, "default_map_zoom": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Ops Lead"
    assert data["notifications_enabled"] is False
    assert data["default_map_zoom"] == 8


def test_update_operator_rejects_unknown_columns() -> None:
    with pytest.raises(ValueError, match="Unknown operator columns"):
        update_operator("op-001", {"theme = 'x' WHERE 1=1; --": "y"})


def test_update_operator_noop_on_empty_updates() -> None:
    before = get_operator("op-001")
    update_operator("op-001", {})
    assert get_operator("op-001") == before
