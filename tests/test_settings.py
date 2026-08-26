from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from src.api.db import OPERATOR_SET_CLAUSES, get_operator, update_operator
from src.api.models import OperatorSettingsUpdate


def test_allowlist_matches_settings_model() -> None:
    assert set(OPERATOR_SET_CLAUSES) == set(OperatorSettingsUpdate.model_fields)


def test_update_operator_rejects_non_allowlisted_key() -> None:
    with pytest.raises(ValueError, match="Unsupported operator column"):
        update_operator("op-001", {"display_name = 'x', theme": "dark"})

    assert get_operator("op-001")["theme"] != "dark"


def test_update_settings_persists_allowlisted_fields(
    client: TestClient, auth_headers: dict[str, str]
) -> None:
    resp = client.patch(
        "/api/v1/settings/",
        headers=auth_headers,
        json={"display_name": "Night Shift", "default_map_zoom": 8},
    )
    assert resp.status_code == 200
    data = resp.json()
    assert data["display_name"] == "Night Shift"
    assert data["default_map_zoom"] == 8
