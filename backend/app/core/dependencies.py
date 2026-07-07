"""Shared FastAPI dependencies."""

from fastapi import Header

from app.shared.trace import set_trace_id


def trace_context(x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")) -> str:
    return set_trace_id(x_trace_id)
