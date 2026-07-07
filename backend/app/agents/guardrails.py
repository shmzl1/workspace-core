"""Agent guardrail declarations."""

FORBIDDEN_DIRECT_IMPORTS = ("app.human_only", "app.core.database")


def assert_agent_boundary(import_path: str) -> None:
    if import_path.startswith(FORBIDDEN_DIRECT_IMPORTS):
        raise ValueError("Agent must call Tool -> Service instead of direct restricted imports.")
