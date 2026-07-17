"""Executable six-node LangGraph orchestration for recruitment decisions."""

from collections.abc import Awaitable, Callable
from typing import Literal, TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.run_store import AgentRunStore
from app.agents.workflows.recruitment_decision.decision_review_agent import (
    decision_review_node,
)
from app.agents.workflows.recruitment_decision.interview_evaluation_agent import (
    interview_evaluation_node,
)
from app.agents.workflows.recruitment_decision.job_match_agent import job_match_node
from app.agents.workflows.recruitment_decision.report_agent import hr_report_node
from app.agents.workflows.recruitment_decision.resume_parser_agent import resume_parser_node
from app.agents.workflows.recruitment_decision.strategy_agent import recruitment_strategy_node

RecruitmentEntrypoint = Literal["full_workflow", "hr_report_only"]


class RecruitmentGraphState(TypedDict, total=False):
    run_id: str
    entrypoint: RecruitmentEntrypoint
    needs_human_review: bool


ExecutableNode = Callable[..., Awaitable[dict[str, object]]]


def route_entrypoint(state: RecruitmentGraphState) -> str:
    if state.get("entrypoint") == "hr_report_only":
        return "hr_report"
    return "recruitment_strategy"


def route_after_decision_review(state: RecruitmentGraphState) -> str:
    return "end" if state.get("needs_human_review") else "hr_report"


def build_agent_graph(
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
):
    """Compile the shared full-workflow and report-only recruitment Graph."""

    builder = StateGraph(RecruitmentGraphState)
    builder.add_node(
        "recruitment_strategy",
        _bind_node(recruitment_strategy_node, store, dependencies),
    )
    builder.add_node(
        "resume_parser",
        _bind_node(resume_parser_node, store, dependencies),
    )
    builder.add_node(
        "job_match",
        _bind_node(job_match_node, store, dependencies),
    )
    builder.add_node(
        "interview_evaluation",
        _bind_node(interview_evaluation_node, store, dependencies),
    )
    builder.add_node(
        "decision_review",
        _bind_node(decision_review_node, store, dependencies),
    )
    builder.add_node(
        "hr_report",
        _bind_node(hr_report_node, store, dependencies),
    )
    builder.add_conditional_edges(
        START,
        route_entrypoint,
        {
            "recruitment_strategy": "recruitment_strategy",
            "hr_report": "hr_report",
        },
    )
    builder.add_edge("recruitment_strategy", "resume_parser")
    builder.add_edge("resume_parser", "job_match")
    builder.add_edge("job_match", "interview_evaluation")
    builder.add_edge("interview_evaluation", "decision_review")
    builder.add_conditional_edges(
        "decision_review",
        route_after_decision_review,
        {"hr_report": "hr_report", "end": END},
    )
    builder.add_edge("hr_report", END)
    return builder.compile()


def _bind_node(
    node: ExecutableNode,
    store: AgentRunStore | None,
    dependencies: RecruitmentRunnerDependencies | None,
) -> Callable[[RecruitmentGraphState], Awaitable[dict[str, object]]]:
    async def invoke(state: RecruitmentGraphState) -> dict[str, object]:
        resolved_store, resolved_dependencies = _resolve_runtime(store, dependencies)
        return await node(
            state,
            store=resolved_store,
            dependencies=resolved_dependencies,
        )

    return invoke


def _resolve_runtime(
    store: AgentRunStore | None,
    dependencies: RecruitmentRunnerDependencies | None,
) -> tuple[AgentRunStore, RecruitmentRunnerDependencies]:
    if store is not None and dependencies is not None:
        return store, dependencies
    from app.core.container import get_application_container

    container = get_application_container()
    return (
        store or container.agent_run_store,
        dependencies or container.recruitment_runner_dependencies,
    )


__all__ = [
    "RecruitmentGraphState",
    "build_agent_graph",
    "route_after_decision_review",
    "route_entrypoint",
]
