"""
Static API key authentication. Explicitly NOT production-grade:
single shared key, no rotation, no per-user scoping, no rate limiting.
Sufficient for a demo/MVP context — say this explicitly in your report
alongside the other named tradeoffs (open Atlas IP whitelist, etc.).
"""

from fastapi import Header, HTTPException, status
from app.config import settings


async def verify_api_key(x_api_key: str = Header(...)):
    if x_api_key != settings.API_KEY:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or missing API key",
        )
    return x_api_key