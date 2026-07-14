"""Declarative boundaries for Agent runtime and Agent node imports."""

from enum import Enum

from pydantic import BaseModel


class AgentBoundaryRule(str, Enum):
    NO_REPOSITORY_ACCESS = "NO_REPOSITORY_ACCESS"
    NO_HUMAN_ONLY_IMPORT = "NO_HUMAN_ONLY_IMPORT"
    TOOL_CALLS_SERVICE_ONLY = "TOOL_CALLS_SERVICE_ONLY"
    NO_AUTOMATED_HIRING_DECISION = "NO_AUTOMATED_HIRING_DECISION"
    NO_AUTOMATED_INTERVIEW_CONFIRMATION = "NO_AUTOMATED_INTERVIEW_CONFIRMATION"
    NO_PAYROLL_CONFIRMATION = "NO_PAYROLL_CONFIRMATION"
    EMPLOYEE_SELF_DATA_ONLY = "EMPLOYEE_SELF_DATA_ONLY"


class AgentGuardrailPolicy(BaseModel):
    rules: tuple[AgentBoundaryRule, ...]


DEFAULT_AGENT_GUARDRAILS = AgentGuardrailPolicy(rules=tuple(AgentBoundaryRule))

FORBIDDEN_DIRECT_IMPORTS = (
    "app.human_only",
    "app.core.database",
    "app.modules.recruitment.repository",
    "app.modules.interview.repository",
    "app.modules.employee.repository",
    "app.modules.payroll.repository",
)


def assert_agent_boundary(import_path: str) -> None:
    """Validate imports made by Agent runtime/nodes, not normal API dependencies."""

    if any(
        import_path == forbidden or import_path.startswith(f"{forbidden}.")
        for forbidden in FORBIDDEN_DIRECT_IMPORTS
    ):
        raise ValueError("Agent must call Tool -> Service instead of a restricted boundary.")

