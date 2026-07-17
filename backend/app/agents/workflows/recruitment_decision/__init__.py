"""Recruitment contracts with lazy compatibility exports for graph metadata."""

from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
__all__ = [
    "RECRUITMENT_WORKFLOW_EDGES",
    "RECRUITMENT_WORKFLOW_NODES",
    "RecruitmentRunRequest",
    "RecruitmentRunSnapshot",
]


def __getattr__(name: str):
    if name in {"RECRUITMENT_WORKFLOW_EDGES", "RECRUITMENT_WORKFLOW_NODES"}:
        from app.agents.workflows.recruitment_decision import graph

        return getattr(graph, name)
    raise AttributeError(name)

