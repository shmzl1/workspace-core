"""Shared runtime support for executable recruitment LangGraph nodes."""

from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import datetime, timezone
from time import perf_counter
from typing import Any
from uuid import uuid4

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.run_store import AgentRunStore, RecruitmentRunRecord
from app.agents.shared import (
    AgentErrorInfo,
    AgentEvent,
    AgentEventType,
    AgentNodeStatus,
    AgentRunStatus,
)
from app.agents.workflows.recruitment_decision.contracts import DecisionReviewSummary

STRATEGY_NODE_NAME = "recruitment_strategy"
RESUME_NODE_NAME = "resume_parser"
JOB_MATCH_NODE_NAME = "job_match"
INTERVIEW_NODE_NAME = "interview_evaluation"
DECISION_REVIEW_NODE_NAME = "decision_review"
REPORT_NODE_NAME = "hr_report"

INTERVIEW_SKIP_REASON = "STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE"
RUN_SCOPE = "SPRINT_2_3_INTEGRATED"
NEXT_PHASE = "END_TO_END_VALIDATION"
KNOWLEDGE_TOOL_NAME = "retrieve_enterprise_knowledge"
RESUME_TOOL_NAME = "extract_candidate_profile"
JOB_MATCH_TOOL_NAME = "evaluate_candidate"
DECISION_REVIEW_TOOL_NAME = "review_candidate_decision"
REPORT_TOOL_NAME = "build_recruitment_report"


class RecruitmentWorkflowExecutionFailed(Exception):
    """Internal signal that stops Graph traversal after failure is persisted."""


@dataclass
class RecruitmentNodeExecution:
    node_name: str
    step: str
    started_at: float
    fallback_used: bool = False


NodeResult = dict[str, Any]
NodeHandler = Callable[
    [RecruitmentRunRecord, RecruitmentNodeExecution],
    Awaitable[NodeResult],
]


async def execute_recruitment_node(
    run_id: str,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
    node_name: str,
    initial_step: str,
    handler: NodeHandler,
) -> NodeResult:
    """Run one business stage and persist one safe workflow failure on error."""

    record = await store.get(run_id)
    execution = RecruitmentNodeExecution(
        node_name=node_name,
        step=initial_step,
        started_at=perf_counter(),
    )
    try:
        return await handler(record, execution)
    except Exception:
        await mark_workflow_failed(run_id, record, store, execution)
        raise RecruitmentWorkflowExecutionFailed from None


async def mark_workflow_failed(
    run_id: str,
    record: RecruitmentRunRecord,
    store: AgentRunStore,
    execution: RecruitmentNodeExecution,
) -> None:
    """Persist the existing safe failure contract exactly once."""

    snapshot = record.snapshot
    state = record.state
    candidate_id = snapshot.current_candidate_id
    fallback_used = execution.fallback_used or (
        state.knowledge_summary is not None
        and state.knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
    )
    error = AgentErrorInfo(
        code="RECRUITMENT_WORKFLOW_FAILED",
        message="招聘决策工作流执行失败。",
        details={
            "failed_node": execution.node_name,
            "failed_step": execution.step,
            "candidate_id": candidate_id,
        },
    )
    snapshot.status = AgentRunStatus.FAILED
    snapshot.current_agent = execution.node_name
    snapshot.current_node = execution.node_name
    snapshot.nodes[execution.node_name] = AgentNodeStatus.FAILED
    snapshot.error = error
    state.status = AgentRunStatus.FAILED
    state.current_agent = execution.node_name
    state.current_node = execution.node_name
    state.node_statuses[execution.node_name] = AgentNodeStatus.FAILED
    state.error = error
    await store.update_snapshot(run_id, snapshot, state)
    await publish(store, event(
        run_id,
        snapshot.trace_id,
        AgentEventType.WORKFLOW_FAILED,
        AgentNodeStatus.FAILED,
        "招聘决策工作流失败",
        {
            "failed_node": execution.node_name,
            "failed_step": execution.step,
            "current_scope": RUN_SCOPE,
        },
        agent_name=execution.node_name,
        node_name=execution.node_name,
        candidate_id=candidate_id,
        duration_ms=elapsed_ms(execution.started_at),
        fallback_used=fallback_used,
        error=error,
    ))


def decision_requires_review(
    review: DecisionReviewSummary,
    confidence_threshold: float,
) -> bool:
    mandatory_review_codes = {
        "DETERMINISTIC_SCORE_UNAVAILABLE",
        "REQUIRED_SKILL_MISSING",
        "INTERVIEW_DATA_MISSING",
        "CONFIDENCE_BELOW_THRESHOLD",
    }
    finding_codes = {finding.code for finding in review.findings}
    return (
        bool(finding_codes & mandatory_review_codes)
        or review.confidence is None
        or review.confidence < confidence_threshold
        or any(finding.severity == "HIGH" for finding in review.findings)
        or any(finding.requires_human_review for finding in review.findings)
    )


async def publish(store: AgentRunStore, agent_event: AgentEvent) -> None:
    await store.append_event(agent_event.run_id, agent_event)


def event(
    run_id: str,
    trace_id: str,
    event_type: AgentEventType,
    status: AgentNodeStatus,
    display_name: str,
    summary: dict[str, object],
    *,
    agent_name: str | None = None,
    node_name: str | None = None,
    candidate_id: int | None = None,
    tool_name: str | None = None,
    source_count: int = 0,
    duration_ms: int | None = None,
    fallback_used: bool = False,
    error: AgentErrorInfo | None = None,
) -> AgentEvent:
    return AgentEvent(
        event_id=uuid4().hex,
        run_id=run_id,
        trace_id=trace_id,
        candidate_id=candidate_id,
        agent_name=agent_name,
        node_name=node_name,
        display_name=display_name,
        event_type=event_type,
        status=status,
        summary=summary,
        tool_name=tool_name,
        source_count=source_count,
        duration_ms=duration_ms,
        fallback_used=fallback_used,
        created_at=datetime.now(timezone.utc),
        error=error,
    )


def elapsed_ms(started_at: float) -> int:
    return max(0, int((perf_counter() - started_at) * 1000))
