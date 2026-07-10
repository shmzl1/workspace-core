"""Static Agent boundary declarations."""

FORBIDDEN_DIRECT_IMPORTS = (
    "app.human_only",
    "app.core.database",
    "app.modules.recruitment.repository",
)


def assert_agent_boundary(import_path: str) -> None:
    if import_path.startswith(FORBIDDEN_DIRECT_IMPORTS):
        raise ValueError("Agent runtime must use validated Service data.")

