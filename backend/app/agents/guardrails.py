"""Compatibility import; new code uses :mod:`app.agents.shared.guardrails`."""

from app.agents.shared.guardrails import (
    DEFAULT_AGENT_GUARDRAILS,
    FORBIDDEN_DIRECT_IMPORTS,
    AgentBoundaryRule,
    AgentGuardrailPolicy,
    assert_agent_boundary,
)

__all__ = [
    "AgentBoundaryRule",
    "AgentGuardrailPolicy",
    "DEFAULT_AGENT_GUARDRAILS",
    "FORBIDDEN_DIRECT_IMPORTS",
    "assert_agent_boundary",
]
