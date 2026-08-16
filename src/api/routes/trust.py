"""Public Trust Center endpoint.

The Trust Center is intentionally unauthenticated: it surfaces the same
security and compliance information we would publish on a public webpage.
"""

from __future__ import annotations

import logging

from fastapi import APIRouter

from src.api.models import TrustCenterResponse
from src.api.trust_content import TRUST_CENTER

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/trust", tags=["trust"])


@router.get("/", response_model=TrustCenterResponse)
def get_trust_center() -> TrustCenterResponse:
    return TrustCenterResponse(**TRUST_CENTER)
