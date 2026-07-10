"""Compatibility trace helpers and shared redaction declarations."""

from app.agents.shared.trace import FORBIDDEN_TRACE_FIELDS, TraceRedactionPolicy
from app.shared.trace import get_trace_id, new_trace_id


def current_agent_trace_id() -> str:
    return get_trace_id() or new_trace_id()


__all__ = ["FORBIDDEN_TRACE_FIELDS", "TraceRedactionPolicy", "current_agent_trace_id"]
