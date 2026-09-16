import importlib
from datetime import datetime, timedelta, timezone

import jwt
import pytest
from fastapi import HTTPException


def test_import_fails_without_jwt_secret(monkeypatch):
    monkeypatch.delenv("JWT_SECRET", raising=False)
    import src.api.auth as auth_mod

    try:
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            importlib.reload(auth_mod)
    finally:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        importlib.reload(auth_mod)


def test_import_fails_with_empty_jwt_secret(monkeypatch):
    import src.api.auth as auth_mod

    try:
        monkeypatch.setenv("JWT_SECRET", "")
        with pytest.raises(RuntimeError, match="JWT_SECRET"):
            importlib.reload(auth_mod)
    finally:
        monkeypatch.setenv("JWT_SECRET", "test-secret")
        importlib.reload(auth_mod)


def test_create_and_decode_roundtrip():
    from src.api.auth import create_token, decode_token

    token = create_token("op-001")
    assert decode_token(token)["sub"] == "op-001"


def test_token_signed_with_old_default_is_rejected():
    from src.api.auth import decode_token

    token = jwt.encode(
        {
            "sub": "op-001",
            "exp": datetime.now(timezone.utc) + timedelta(hours=1),
        },
        "dev-secret-do-not-use",
        algorithm="HS256",
    )
    with pytest.raises(HTTPException) as exc_info:
        decode_token(token)
    assert exc_info.value.status_code == 401
