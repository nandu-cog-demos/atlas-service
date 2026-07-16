from __future__ import annotations

import pytest

from src.api.auth import _load_jwt_secret


def test_load_jwt_secret_missing(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        _load_jwt_secret()


def test_load_jwt_secret_present(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("JWT_SECRET", "some-secret")
    assert _load_jwt_secret() == "some-secret"
