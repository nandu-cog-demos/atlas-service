"""Token-based authentication for operators and devices."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timedelta, timezone

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer

logger = logging.getLogger(__name__)


def _load_jwt_secret() -> str:
    secret = os.getenv("JWT_SECRET")
    if not secret:
        raise RuntimeError(
            "JWT_SECRET environment variable is not set; refusing to start "
            "with an unconfigured signing secret"
        )
    return secret


JWT_SECRET = _load_jwt_secret()
JWT_ALGORITHM = "HS256"
TOKEN_EXPIRY_HOURS = 24

_bearer_scheme = HTTPBearer()


def create_token(operator_id: str) -> str:
    payload = {
        "sub": operator_id,
        "iat": datetime.now(timezone.utc),
        "exp": datetime.now(timezone.utc) + timedelta(hours=TOKEN_EXPIRY_HOURS),
    }
    return jwt.encode(payload, JWT_SECRET, algorithm=JWT_ALGORITHM)


def decode_token(token: str) -> dict:
    try:
        return jwt.decode(token, JWT_SECRET, algorithms=[JWT_ALGORITHM])
    except jwt.ExpiredSignatureError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token has expired",
        )
    except jwt.InvalidTokenError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid token",
        )


def get_current_operator(
    credentials: HTTPAuthorizationCredentials = Depends(_bearer_scheme),
) -> str:
    payload = decode_token(credentials.credentials)
    operator_id: str | None = payload.get("sub")
    if not operator_id:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token missing subject",
        )
    logger.debug("Authenticated operator %s", operator_id)
    return operator_id
