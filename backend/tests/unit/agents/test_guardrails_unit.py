import pytest

from app.agents.shared.guardrails import (
    AgentBoundaryRule,
    DEFAULT_AGENT_GUARDRAILS,
    assert_agent_boundary,
)


def test_default_policy_contains_every_boundary_rule() -> None:
    assert DEFAULT_AGENT_GUARDRAILS.rules == tuple(AgentBoundaryRule)


@pytest.mark.parametrize(
    "import_path",
    [
        "app.human_only",
        "app.human_only.resume_scoring",
        "app.core.database",
        "app.core.database.session",
        "app.modules.recruitment.repository",
        "app.modules.interview.repository.helpers",
        "app.modules.employee.repository",
        "app.modules.payroll.repository.query",
    ],
)
def test_restricted_module_and_descendants_are_rejected(import_path: str) -> None:
    with pytest.raises(ValueError, match="Tool -> Service"):
        assert_agent_boundary(import_path)


@pytest.mark.parametrize(
    "import_path",
    [
        "app.core.database_helpers",
        "app.human_only_adapter",
        "app.modules.recruitment.repository_cache",
        "app.modules.interview.repository_v2",
        "app.modules.recruitment.service",
        "app.agents.tools.recruitment_tools",
        "",
    ],
)
def test_similar_but_distinct_module_names_are_allowed(import_path: str) -> None:
    assert_agent_boundary(import_path)
