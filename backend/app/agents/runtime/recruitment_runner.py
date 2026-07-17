"""Public recruitment scheduling API backed by the executable LangGraph."""

import asyncio

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.recruitment_support import (
    DECISION_REVIEW_NODE_NAME,
    INTERVIEW_NODE_NAME,
    INTERVIEW_SKIP_REASON,
    JOB_MATCH_NODE_NAME,
    REPORT_NODE_NAME,
    RESUME_NODE_NAME,
    STRATEGY_NODE_NAME,
    RecruitmentWorkflowExecutionFailed,
    decision_requires_review,
)
from app.agents.runtime.run_store import AgentRunStore
from app.agents.workflows.recruitment_decision.contracts import RecruitmentRunContext

STRATEGY_NODE = STRATEGY_NODE_NAME
RESUME_NODE = RESUME_NODE_NAME
JOB_MATCH_NODE = JOB_MATCH_NODE_NAME
INTERVIEW_NODE = INTERVIEW_NODE_NAME
DECISION_REVIEW_NODE = DECISION_REVIEW_NODE_NAME
REPORT_NODE = REPORT_NODE_NAME
_decision_requires_review = decision_requires_review
_RUNNING_TASKS: set[asyncio.Task[None]] = set()


def schedule_recruitment_strategy_run(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    task = asyncio.create_task(
        run_recruitment_strategy(
            run_id,
            context,
            resolved_store,
            resolved_dependencies,
        )
    )
    _RUNNING_TASKS.add(task)
    task.add_done_callback(_RUNNING_TASKS.discard)


async def run_recruitment_strategy(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    """Run the six-node full-workflow entrypoint without changing its public API."""

    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    await _invoke_recruitment_graph(
        run_id,
        "full_workflow",
        resolved_store,
        resolved_dependencies,
    )


async def _run_recruitment_pipeline(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> None:
    """Compatibility wrapper; the pipeline now traverses six real Graph nodes."""

    await _invoke_recruitment_graph(
        run_id,
        "full_workflow",
        store,
        dependencies,
    )


def schedule_hr_report_stage(
    run_id: str,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    """Schedule one persisted Run's HR report stage after HR approval."""

    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    task = asyncio.create_task(
        run_hr_report_stage(run_id, resolved_store, resolved_dependencies)
    )
    _RUNNING_TASKS.add(task)
    task.add_done_callback(_RUNNING_TASKS.discard)


async def run_hr_report_stage(
    run_id: str,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    """Run the report-only entrypoint through the same compiled LangGraph."""

    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    await _invoke_recruitment_graph(
        run_id,
        "hr_report_only",
        resolved_store,
        resolved_dependencies,
    )


async def _invoke_recruitment_graph(
    run_id: str,
    entrypoint: str,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> None:
    from app.agents.graph_factory import build_agent_graph

    graph = build_agent_graph(store, dependencies)
    try:
        await graph.ainvoke({"run_id": run_id, "entrypoint": entrypoint})
    except RecruitmentWorkflowExecutionFailed:
        return


def _default_dependencies() -> RecruitmentRunnerDependencies:
    from app.core.container import get_application_container

    return get_application_container().recruitment_runner_dependencies


def _default_store() -> AgentRunStore:
    from app.core.container import get_application_container

    return get_application_container().agent_run_store


__all__ = [
    "DECISION_REVIEW_NODE",
    "INTERVIEW_NODE",
    "INTERVIEW_SKIP_REASON",
    "JOB_MATCH_NODE",
    "REPORT_NODE",
    "RESUME_NODE",
    "STRATEGY_NODE",
    "run_hr_report_stage",
    "run_recruitment_strategy",
    "schedule_hr_report_stage",
    "schedule_recruitment_strategy_run",
]
