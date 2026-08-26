from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def _import_auth(env: dict[str, str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-c", "import src.api.auth"],
        env=env,
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    )


def test_startup_fails_without_jwt_secret() -> None:
    env = {k: v for k, v in os.environ.items() if k != "JWT_SECRET"}
    result = _import_auth(env)
    assert result.returncode != 0
    assert "JWT_SECRET" in result.stderr


def test_startup_fails_with_empty_jwt_secret() -> None:
    env = {**os.environ, "JWT_SECRET": ""}
    result = _import_auth(env)
    assert result.returncode != 0
    assert "JWT_SECRET" in result.stderr


def test_startup_succeeds_with_jwt_secret() -> None:
    env = {**os.environ, "JWT_SECRET": "test-secret"}
    result = _import_auth(env)
    assert result.returncode == 0, result.stderr
