"""Small serialization helpers for API-facing services."""

from datetime import date, datetime, time
from decimal import Decimal
from typing import Any


def scalar(value: Any) -> Any:
    if isinstance(value, Decimal):
        return str(value)
    if isinstance(value, datetime | date | time):
        return value.isoformat()
    return value


def model_to_dict(model: Any, fields: list[str]) -> dict[str, Any]:
    return {field: scalar(getattr(model, field)) for field in fields}
