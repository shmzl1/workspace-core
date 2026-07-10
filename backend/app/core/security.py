"""JWT and presentation-safe security helpers."""

from datetime import datetime, timedelta, timezone
from typing import Any

from jose import jwt

from app.core.config import get_settings


def create_access_token(subject: dict[str, Any], expires_delta: timedelta) -> str:
    payload = dict(subject)
    payload["exp"] = datetime.now(timezone.utc) + expires_delta
    settings = get_settings()
    return jwt.encode(payload, settings.jwt_secret_key, algorithm=settings.jwt_algorithm)


def mask_sensitive(value: str | None, visible_tail: int = 4) -> str | None:
    if value is None:
        return None
    if len(value) <= visible_tail:
        return "*" * len(value)
    return "*" * (len(value) - visible_tail) + value[-visible_tail:]
