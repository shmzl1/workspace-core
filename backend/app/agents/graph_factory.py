"""LangGraph orchestration entry point for the recruitment workflow."""

from functools import lru_cache
from typing import TypedDict

from langgraph.graph import END, START, StateGraph

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.run_store import AgentRunStore
from app.agents.workflows.recruitment_decision.contracts import RecruitmentRunContext


class RecruitmentGraphState(TypedDict, total=False):
    run_id: str
    context: RecruitmentRunContext
    store: AgentRunStore
    dependencies: RecruitmentRunnerDependencies
    runnable: bool
    completed: bool


async def prepare_run(state: RecruitmentGraphState) -> dict[str, bool]:
    """Check that the already-created run has everything needed to execute."""
    runnable = bool(state.get("run_id")) and all(
        state.get(key) is not None for key in ("context", "store", "dependencies")
    )
    return {"runnable": runnable}


def route_after_prepare(state: RecruitmentGraphState) -> str:
    return "execute" if state.get("runnable") else "end"


async def execute_recruitment_pipeline(
    state: RecruitmentGraphState,
) -> dict[str, bool]:
    # Keep this import local so the public runner can import the graph factory.
    from app.agents.runtime.recruitment_runner import _run_recruitment_pipeline

    await _run_recruitment_pipeline(
        state["run_id"],
        state["context"],
        state["store"],
        state["dependencies"],
    )
    return {"completed": True}


@lru_cache(maxsize=1)
def build_agent_graph():
    builder = StateGraph(RecruitmentGraphState)
    builder.add_node("prepare_run", prepare_run)
    builder.add_node("execute_recruitment_pipeline", execute_recruitment_pipeline)
    builder.add_edge(START, "prepare_run")
    builder.add_conditional_edges(
        "prepare_run",
        route_after_prepare,
        {"execute": "execute_recruitment_pipeline", "end": END},
    )
    builder.add_edge("execute_recruitment_pipeline", END)
    return builder.compile()


__all__ = ["RecruitmentGraphState", "build_agent_graph"]
