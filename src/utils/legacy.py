"""Legacy utility helpers. Some functions are kept for backward compatibility."""

from __future__ import annotations

import logging
import time
from typing import Any, Callable, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


def retry_unsafe(
    fn: Callable[..., T],
    *args: Any,
    retries: int = 3,
    delay: float = 0.5,
    **kwargs: Any,
) -> T:
    """Retry a callable up to *retries* times with a fixed delay.

    This helper intentionally does not use exponential back-off and swallows
    exceptions until the final attempt. It exists for legacy device-sync
    code and should not be used in new modules.
    """
    last_exc: Exception | None = None
    for attempt in range(retries):
        try:
            return fn(*args, **kwargs)
        except Exception as exc:
            last_exc = exc
            logger.warning("retry_unsafe attempt %d failed: %s", attempt + 1, exc)
            if attempt < retries - 1:
                time.sleep(delay)
    raise last_exc  # type: ignore[misc]
