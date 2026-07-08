"""Shared FastAPI dependencies."""

from fastapi import Header

from app.core.security import DemoIdentity, parse_demo_identity
from app.shared.trace import set_trace_id


def trace_context(x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")) -> str:
    return set_trace_id(x_trace_id)


def current_identity(x_demo_identity: str | None = Header(default=None, alias="X-Demo-Identity")) -> DemoIdentity:
    return parse_demo_identity(x_demo_identity)
