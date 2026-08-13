from __future__ import annotations

import importlib

import pytest

from src.api import auth


def test_create_and_decode_token_roundtrip(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "roundtrip-secret")
    token = auth.create_token("op-001")
    payload = auth.decode_token(token)
    assert payload["sub"] == "op-001"


def test_get_jwt_secret_missing_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        auth.get_jwt_secret()


def test_get_jwt_secret_empty_raises(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "")
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        auth.get_jwt_secret()


def test_create_token_missing_secret_raises(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        auth.create_token("op-001")


def test_decode_token_missing_secret_raises(monkeypatch):
    monkeypatch.setenv("JWT_SECRET", "some-secret")
    token = auth.create_token("op-001")
    monkeypatch.delenv("JWT_SECRET", raising=False)
    with pytest.raises(RuntimeError, match="JWT_SECRET"):
        auth.decode_token(token)


def test_app_import_fails_without_secret(monkeypatch):
    from src.api import main

    monkeypatch.delenv("JWT_SECRET", raising=False)
    try:
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            importlib.reload(main)
    finally:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        importlib.reload(main)
