"""Authenticated persistent recruitment Agent Run endpoints.

The existing in-process Run, owner isolation and raw ``AgentEvent`` SSE contract
remain unchanged. The current phase adds deterministic job matching, rule-based
decision review and a structured HR report; interview evaluation is skipped when
real structured feedback is unavailable.
"""

import asyncio
from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.runtime.event_stream import create_agent_event_stream
from app.agents.runtime.recruitment_runner import (
    DECISION_REVIEW_NODE,
    JOB_MATCH_NODE,
    REPORT_NODE,
    schedule_hr_report_stage,
    schedule_recruitment_strategy_run,
)
from app.agents.shared import AgentEvent, AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.core.exceptions import TalentFlowError
from app.core.container import ApplicationContainer, get_application_container
from app.modules.auth.models import User
from app.modules.interview.service import InterviewService
from app.modules.recruitment.service import RecruitmentService
from app.modules.recruitment.services import RecruitmentRunContextService
from app.shared.response import ApiResponse, ok
from app.shared.trace import get_trace_id, new_trace_id

router = APIRouter()
_REVIEW_APPROVAL_LOCKS: dict[str, asyncio.Lock] = {}


@router.post("/recruitment/runs", response_model=ApiResponse[RecruitmentRunSnapshot])
async def create_recruitment_run(
    payload: RecruitmentRunRequest,
    current_user: User = Depends(require_permission("agent.hr.use")),
    session: Session = Depends(get_db_session),
    container: ApplicationContainer = Depends(get_application_container),
) -> ApiResponse[RecruitmentRunSnapshot]:
    """Create a PostgreSQL-backed recruitment Agent Run."""

    context_service = RecruitmentRunContextService(
        RecruitmentService.from_session(session),
        InterviewService.from_session(session),
    )
    context = context_service.validate(payload)
    now = datetime.now(timezone.utc)
    run_id = uuid4().hex
    trace_id = get_trace_id() or new_trace_id()
    initial_nodes = {node.name: AgentNodeStatus.WAITING for node in RECRUITMENT_WORKFLOW_NODES}
    state = RecruitmentDecisionState(
        run_id=run_id,
        trace_id=trace_id,
        actor_user_id=current_user.id,
        context=context,
        node_statuses=initial_nodes.copy(),
    )
    snapshot = RecruitmentRunSnapshot(
        run_id=run_id,
        trace_id=trace_id,
        status=AgentRunStatus.PENDING,
        goal=context.request.goal,
        job=context.job,
        candidate_ids=context.candidate_ids,
        total_candidates=len(context.candidate_ids),
        nodes=initial_nodes,
        created_at=now,
        updated_at=now,
    )
    await container.agent_run_store.create(current_user.id, state, snapshot)
    schedule_recruitment_strategy_run(
        run_id,
        context,
        container.agent_run_store,
        container.recruitment_runner_dependencies,
    )
    return ok(snapshot, trace_id)


@router.get("/recruitment/runs/{run_id}", response_model=ApiResponse[RecruitmentRunSnapshot])
async def get_recruitment_run(
    run_id: str,
    current_user: User = Depends(require_permission("agent.hr.use")),
    container: ApplicationContainer = Depends(get_application_container),
) -> ApiResponse[RecruitmentRunSnapshot]:
    """Return the current owner's persisted Run snapshot."""

    record = await container.agent_run_store.get_owned(run_id, current_user.id)
    return ok(record.snapshot, record.snapshot.trace_id)


@router.post(
    "/recruitment/runs/{run_id}/approve-job-match-review",
    response_model=ApiResponse[RecruitmentRunSnapshot],
)
async def approve_job_match_review(
    run_id: str,
    current_user: User = Depends(require_permission("agent.hr.use")),
    container: ApplicationContainer = Depends(get_application_container),
) -> ApiResponse[RecruitmentRunSnapshot]:
    """Record HR approval for the job-match review only."""

    return await _approve_recruitment_review_node(
        run_id,
        JOB_MATCH_NODE,
        "岗位匹配结果",
        current_user,
        container,
    )


@router.post(
    "/recruitment/runs/{run_id}/approve-decision-review",
    response_model=ApiResponse[RecruitmentRunSnapshot],
)
async def approve_decision_review(
    run_id: str,
    current_user: User = Depends(require_permission("agent.hr.use")),
    container: ApplicationContainer = Depends(get_application_container),
) -> ApiResponse[RecruitmentRunSnapshot]:
    """Record HR approval for the decision review only."""

    return await _approve_recruitment_review_node(
        run_id,
        DECISION_REVIEW_NODE,
        "决策审查结果",
        current_user,
        container,
    )


async def _approve_recruitment_review_node(
    run_id: str,
    node_name: str,
    node_display_name: str,
    current_user: User,
    container: ApplicationContainer,
) -> ApiResponse[RecruitmentRunSnapshot]:
    lock = _REVIEW_APPROVAL_LOCKS.setdefault(run_id, asyncio.Lock())
    async with lock:
        record = await container.agent_run_store.get_owned(run_id, current_user.id)
        snapshot = record.snapshot
        state = record.state
        is_pending_review = (
            snapshot.status is AgentRunStatus.RUNNING
            and snapshot.report is None
            and snapshot.nodes.get(REPORT_NODE) is AgentNodeStatus.WAITING
            and snapshot.nodes.get(node_name) is AgentNodeStatus.NEEDS_REVIEW
        )
        if not is_pending_review:
            raise TalentFlowError(
                "RECRUITMENT_REVIEW_NOT_PENDING",
                "当前招聘运行不处于待人工审查状态，不能重复提交审查通过。",
                409,
            )

        snapshot.nodes[node_name] = AgentNodeStatus.COMPLETED
        state.node_statuses[node_name] = AgentNodeStatus.COMPLETED
        snapshot.current_agent = None
        snapshot.current_node = None
        snapshot.current_candidate_id = None
        state.current_agent = None
        state.current_node = None
        state.current_candidate_id = None
        updated_record = await container.agent_run_store.update_snapshot(run_id, snapshot, state)

        review_nodes_still_pending = [
            name
            for name in (JOB_MATCH_NODE, DECISION_REVIEW_NODE)
            if snapshot.nodes.get(name) is AgentNodeStatus.NEEDS_REVIEW
        ]
        will_generate_report = not review_nodes_still_pending
        await container.agent_run_store.append_event(
            run_id,
            AgentEvent(
                event_id=uuid4().hex,
                run_id=run_id,
                trace_id=updated_record.snapshot.trace_id,
                agent_name=node_name,
                node_name=node_name,
                display_name=f"HR 已审查通过{node_display_name}",
                event_type=AgentEventType.REVIEW_COMPLETED,
                status=AgentNodeStatus.COMPLETED,
                summary={
                    "human_review_approved": True,
                    "approved_by_user_id": current_user.id,
                    "approved_nodes": [node_name],
                    "next_action": "生成 HR 最终报告"
                    if will_generate_report
                    else "等待 HR 审查通过其余审查结果",
                },
                created_at=datetime.now(timezone.utc),
            ),
        )

        response_snapshot = (await container.agent_run_store.get_owned(run_id, current_user.id)).snapshot
        if will_generate_report:
            schedule_hr_report_stage(
                run_id,
                container.agent_run_store,
                container.recruitment_runner_dependencies,
            )
        return ok(response_snapshot, response_snapshot.trace_id)


@router.get(
    "/recruitment/runs/{run_id}/events",
    response_class=StreamingResponse,
    response_model=None,
)
async def stream_recruitment_run_events(
    run_id: str,
    request: Request,
    current_user: User = Depends(require_permission("agent.hr.use")),
    container: ApplicationContainer = Depends(get_application_container),
) -> StreamingResponse:
    """Stream the current owner's Run as raw ``AgentEvent`` SSE messages."""

    await container.agent_run_store.get_owned(run_id, current_user.id)
    return create_agent_event_stream(request, run_id, current_user.id, container.agent_run_store)
