"""Compatibility import; new code uses :mod:`app.agents.shared.guardrails`."""

from app.agents.shared.guardrails import FORBIDDEN_DIRECT_IMPORTS, assert_agent_boundary

__all__ = ["FORBIDDEN_DIRECT_IMPORTS", "assert_agent_boundary"]
