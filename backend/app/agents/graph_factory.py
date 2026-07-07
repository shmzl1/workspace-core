"""Agent graph factory boundary.

Real LLM wiring is intentionally absent. Agents must use Tool -> Service and
must not import repositories or human_only modules directly.
"""


def build_agent_graph() -> None:
    return None
