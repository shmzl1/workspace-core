"""Trace id helpers shared by API, services and agent tooling."""

from contextvars import ContextVar
from uuid import uuid4

TRACE_ID_HEADER = "X-Trace-Id"
_trace_id: ContextVar[str | None] = ContextVar("trace_id", default=None)


def new_trace_id() -> str:
    return uuid4().hex


def set_trace_id(trace_id: str | None) -> str:
    value = trace_id or new_trace_id()
    _trace_id.set(value)
    return value


def get_trace_id() -> str | None:
    return _trace_id.get()
