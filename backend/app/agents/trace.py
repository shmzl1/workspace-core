"""Agent trace helpers."""

from app.shared.trace import get_trace_id, new_trace_id


def current_agent_trace_id() -> str:
    return get_trace_id() or new_trace_id()
