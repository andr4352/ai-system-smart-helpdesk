import os
import secrets
from fastapi import Header, HTTPException

def require_key(x_api_key: str | None = Header(default=None)):
    expected = os.getenv("API_KEY")
    if not expected:
        raise HTTPException(503, "AUTH_NOT_CONFIGURED")
    if not x_api_key or not secrets.compare_digest(x_api_key, expected):
        raise HTTPException(401, "INVALID_API_KEY")
