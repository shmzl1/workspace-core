"""Deprecated compatibility boundary for the pre-runtime graph factory.

Sprint 2.1 deliberately has no executable LangGraph.  The legacy function is
kept importable while returning ``None`` exactly as the former placeholder did.
"""


def build_agent_graph() -> None:
    return None


__all__ = ["build_agent_graph"]
