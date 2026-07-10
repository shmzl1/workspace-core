"""Authenticated Sprint 2.1 recruitment Agent Run endpoints."""

from datetime import datetime, timezone
from uuid import uuid4

from fastapi import APIRouter, Depends, Request
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session

from app.agents.runtime.event_stream import create_agent_event_stream
from app.agents.runtime.recruitment_runner import schedule_recruitment_strategy_run
from app.agents.runtime.run_store import agent_run_store
from app.agents.shared import AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.modules.auth.models import User
from app.modules.recruitment.service import RecruitmentService
from app.modules.recruitment.services import RecruitmentRunContextService
from app.shared.response import ApiResponse, ok
from app.shared.trace import get_trace_id, new_trace_id

router = APIRouter()


@router.post("/recruitment/runs", response_model=ApiResponse[RecruitmentRunSnapshot])
async def create_recruitment_run(
    payload: RecruitmentRunRequest,
    current_user: User = Depends(require_permission("agent.hr.use")),
    session: Session = Depends(get_db_session),
) -> ApiResponse[RecruitmentRunSnapshot]:
    context_service = RecruitmentRunContextService(RecruitmentService.from_session(session))
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
        total_candidates=len(context.candidate_ids),
        nodes=initial_nodes,
        created_at=now,
        updated_at=now,
    )
    await agent_run_store.create(current_user.id, state, snapshot)
    schedule_recruitment_strategy_run(run_id, context)
    return ok(snapshot, trace_id)


@router.get("/recruitment/runs/{run_id}", response_model=ApiResponse[RecruitmentRunSnapshot])
async def get_recruitment_run(
    run_id: str,
    current_user: User = Depends(require_permission("agent.hr.use")),
) -> ApiResponse[RecruitmentRunSnapshot]:
    record = await agent_run_store.get_owned(run_id, current_user.id)
    return ok(record.snapshot, record.snapshot.trace_id)


@router.get(
    "/recruitment/runs/{run_id}/events",
    response_class=StreamingResponse,
    response_model=None,
)
async def stream_recruitment_run_events(
    run_id: str,
    request: Request,
    current_user: User = Depends(require_permission("agent.hr.use")),
) -> StreamingResponse:
    await agent_run_store.get_owned(run_id, current_user.id)
    return create_agent_event_stream(request, run_id, current_user.id, agent_run_store)
