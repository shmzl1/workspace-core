"""Sprint 2.3 runtime, compatibility, permission and SSE acceptance tests."""

import asyncio
from datetime import date, datetime, timezone
from pathlib import Path

import pytest

from app.agents.runtime.event_stream import create_agent_event_stream
from app.agents.runtime.recruitment_runner import run_recruitment_strategy
from app.agents.runtime.run_store import InMemoryAgentRunStore
from app.agents.shared import AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentDecisionState,
    RecruitmentCandidateContext,
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.core.exceptions import TalentFlowError


def build_context() -> RecruitmentRunContext:
    goal = RecruitmentGoal(
        job_id=1,
        job_title="AI Agent 后端工程师",
        department="技术部",
        target_headcount=1,
        required_skills=["Python"],
        optional_salary_budget=30000,
    )
    return RecruitmentRunContext(
        request=RecruitmentRunRequest(goal=goal, candidate_ids=[101, 102]),
        job=RecruitmentJobContext(
            job_id=1,
            job_code="JOB-AI-001",
            job_title=goal.job_title,
            department=goal.department,
            status="OPEN",
            description="负责 Agent 后端开发",
            required_skills=["Python"],
            preferred_skills=["FastAPI"],
            min_experience_months=24,
            source_version="job-test-v1",
            effective_date=date(2026, 7, 10),
        ),
        candidate_ids=[101, 102],
        application_ids=[201, 202],
        candidates=[
            RecruitmentCandidateContext(
                candidate_id=101,
                application_id=201,
                skills=["Python", "FastAPI"],
                experience_months=36,
                education=["本科"],
                projects=["Agent 平台"],
                resume_excerpt="三年 Python 与 FastAPI 项目经验。",
            ),
            RecruitmentCandidateContext(
                candidate_id=102,
                application_id=202,
                skills=["Python"],
                experience_months=18,
                resume_excerpt="熟悉 Python 开发。",
            ),
        ],
        interview_candidate_ids=[101],
    )


def build_models(run_id: str = "run-sprint-2-1") -> tuple[RecruitmentDecisionState, RecruitmentRunSnapshot]:
    context = build_context()
    now = datetime.now(timezone.utc)
    nodes = {node.name: AgentNodeStatus.WAITING for node in RECRUITMENT_WORKFLOW_NODES}
    state = RecruitmentDecisionState(
        run_id=run_id,
        trace_id="trace-sprint-2-1",
        actor_user_id=7,
        context=context,
        node_statuses=nodes.copy(),
    )
    snapshot = RecruitmentRunSnapshot(
        run_id=run_id,
        trace_id=state.trace_id,
        status=AgentRunStatus.PENDING,
        goal=context.request.goal,
        job=context.job,
        candidate_ids=context.candidate_ids,
        total_candidates=len(context.candidate_ids),
        nodes=nodes,
        created_at=now,
        updated_at=now,
    )
    return state, snapshot


def test_compatibility_and_intelligence_packages_import() -> None:
    from app.agents import graph_factory, guardrails, state, trace
    from app.agents.tools import (
        EMPLOYEE_TOOL_CONTRACTS,
        get_my_annual_leave_balance,
        get_my_monthly_attendance_summary,
        get_my_salary_details,
    )
    from app.modules.recruitment import intelligence

    assert graph_factory.build_agent_graph() is None
    assert guardrails.DEFAULT_AGENT_GUARDRAILS.rules
    assert state.AgentState
    assert trace.current_agent_trace_id()
    assert EMPLOYEE_TOOL_CONTRACTS
    assert callable(get_my_annual_leave_balance)
    assert callable(get_my_monthly_attendance_summary)
    assert callable(get_my_salary_details)
    assert intelligence.ResumeExtractionResult


def test_sprint_2_3_runner_executes_deterministic_intermediate_workflow() -> None:
    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models()
        assert snapshot.nodes["recruitment_strategy"] is AgentNodeStatus.WAITING
        await store.create(7, state, snapshot)

        await run_recruitment_strategy(snapshot.run_id, state.context, store)
        record = await store.get_owned(snapshot.run_id, 7)

        event_types = [event.event_type for event in record.events]
        assert event_types[0] is AgentEventType.WORKFLOW_STARTED
        assert AgentEventType.PLAN_CREATED in event_types
        assert AgentEventType.KNOWLEDGE_RETRIEVED in event_types
        assert event_types.count(AgentEventType.CANDIDATE_COMPLETED) == 2
        assert event_types[-1] is AgentEventType.WORKFLOW_COMPLETED
        assert record.snapshot.status is AgentRunStatus.COMPLETED
        assert record.snapshot.nodes["recruitment_strategy"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["resume_parser"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["job_match"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["interview_evaluation"] is AgentNodeStatus.SKIPPED
        assert record.snapshot.nodes["decision_review"] is AgentNodeStatus.NEEDS_REVIEW
        assert record.snapshot.nodes["hr_report"] is AgentNodeStatus.COMPLETED
        thinking = next(event for event in record.events if event.event_type is AgentEventType.AGENT_THINKING)
        assert "optional_salary_budget" not in thinking.summary["current_goal"]
        assert {event.tool_name for event in record.events if event.tool_name} == {
            "retrieve_enterprise_knowledge",
            "extract_candidate_profile",
            "evaluate_candidate",
            "review_candidate_decision",
            "build_recruitment_report",
        }
        assert record.snapshot.completed_candidates == 2
        assert len(record.snapshot.candidate_profiles) == 2
        assert len(record.snapshot.job_matches) == 2
        assert record.snapshot.interview_evaluations == {}
        assert len(record.snapshot.decision_reviews) == 2
        assert record.snapshot.report is not None
        assert record.snapshot.report.requires_human_decision is True
        assert all(
            any(finding.code == "INTERVIEW_DATA_MISSING" for finding in review.findings)
            for review in record.snapshot.decision_reviews.values()
        )
        assert record.snapshot.knowledge_summary is not None
        assert record.snapshot.knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
        assert record.snapshot.sources
        assert "resume_excerpt" not in record.snapshot.model_dump_json()

        job_match_events = [
            event.event_type for event in record.events if event.node_name == "job_match"
        ]
        assert job_match_events == [
            AgentEventType.AGENT_STARTED,
            AgentEventType.AGENT_THINKING,
            AgentEventType.TOOL_STARTED,
            AgentEventType.TOOL_COMPLETED,
            AgentEventType.INTERMEDIATE_RESULT,
            AgentEventType.TOOL_STARTED,
            AgentEventType.TOOL_COMPLETED,
            AgentEventType.INTERMEDIATE_RESULT,
            AgentEventType.AGENT_COMPLETED,
        ]
        review_events = [
            event.event_type for event in record.events if event.node_name == "decision_review"
        ]
        assert review_events == [
            AgentEventType.AGENT_STARTED,
            AgentEventType.AGENT_THINKING,
            AgentEventType.TOOL_STARTED,
            AgentEventType.TOOL_COMPLETED,
            AgentEventType.REVIEW_COMPLETED,
            AgentEventType.TOOL_STARTED,
            AgentEventType.TOOL_COMPLETED,
            AgentEventType.REVIEW_COMPLETED,
            AgentEventType.AGENT_COMPLETED,
        ]
        report_events = [
            event.event_type for event in record.events if event.node_name == "hr_report"
        ]
        assert report_events == [
            AgentEventType.AGENT_STARTED,
            AgentEventType.AGENT_THINKING,
            AgentEventType.TOOL_STARTED,
            AgentEventType.TOOL_COMPLETED,
            AgentEventType.REPORT_GENERATED,
            AgentEventType.AGENT_COMPLETED,
        ]
        workflow_summary = record.events[-1].summary
        assert workflow_summary["current_scope"] == "SPRINT_2_3_INTEGRATED"
        assert workflow_summary["skip_reasons"] == {
            "interview_evaluation": "STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE"
        }
        assert workflow_summary["report_generated"] is True
        assert workflow_summary["review_required_candidates"] == 2

    asyncio.run(scenario())


def test_run_owner_isolation_and_agent_permission() -> None:
    from app.core.dependencies import require_permission
    from app.modules.auth.models import User

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("owned-run")
        await store.create(7, state, snapshot)
        assert (await store.get_owned(snapshot.run_id, 7)).owner_user_id == 7
        with pytest.raises(TalentFlowError) as exc_info:
            await store.get_owned(snapshot.run_id, 8)
        assert exc_info.value.code == "AGENT_RUN_NOT_FOUND"

    asyncio.run(scenario())

    permission = require_permission("agent.hr.use")
    allowed = User(id=7, username="hr", password_hash="x", role="HR_SPECIALIST", permissions=["agent.hr.use"])
    denied = User(id=8, username="employee", password_hash="x", role="EMPLOYEE", permissions=[])
    assert permission(allowed) is allowed
    with pytest.raises(TalentFlowError) as exc_info:
        permission(denied)
    assert exc_info.value.code == "PERMISSION_DENIED"


def test_sse_replays_history_and_closes_after_terminal_event() -> None:
    class ConnectedRequest:
        async def is_disconnected(self) -> bool:
            return False

    async def scenario() -> list[str]:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("sse-run")
        await store.create(7, state, snapshot)
        await run_recruitment_strategy(snapshot.run_id, state.context, store)
        response = create_agent_event_stream(ConnectedRequest(), snapshot.run_id, 7, store)  # type: ignore[arg-type]
        return [chunk async for chunk in response.body_iterator]

    chunks = asyncio.run(asyncio.wait_for(scenario(), timeout=2))
    assert len(chunks) > 6
    assert all("event: agent_event" in chunk for chunk in chunks)
    assert any("KNOWLEDGE_RETRIEVED" in chunk for chunk in chunks)
    assert sum("CANDIDATE_COMPLETED" in chunk for chunk in chunks) == 2
    assert "WORKFLOW_COMPLETED" in chunks[-1]


def test_failure_event_contains_safe_node_and_step(monkeypatch: pytest.MonkeyPatch) -> None:
    from app.agents.runtime import recruitment_runner

    def fail_plan(*_args: object, **_kwargs: object) -> None:
        raise RuntimeError("sensitive internal failure")

    monkeypatch.setattr(recruitment_runner, "build_recruitment_execution_plan", fail_plan)

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("failed-run")
        await store.create(7, state, snapshot)
        await recruitment_runner.run_recruitment_strategy(snapshot.run_id, state.context, store)
        record = await store.get(snapshot.run_id)
        failure = record.events[-1]
        assert failure.event_type is AgentEventType.WORKFLOW_FAILED
        assert failure.summary["failed_node"] == "recruitment_strategy"
        assert failure.summary["failed_step"] == "build_execution_plan"
        assert failure.error is not None
        assert failure.error.details["failed_step"] == "build_execution_plan"
        assert "sensitive internal failure" not in failure.model_dump_json()

    asyncio.run(scenario())


def test_agent_runtime_and_tools_do_not_import_repositories_or_human_only() -> None:
    agents_root = Path(__file__).resolve().parents[2] / "app" / "agents"
    checked_dirs = [agents_root / "runtime", agents_root / "workflows", agents_root / "tools"]
    for directory in checked_dirs:
        for path in directory.rglob("*.py"):
            source = path.read_text(encoding="utf-8")
            assert ".repository import" not in source, f"{path} imports a Repository"
            assert "app.human_only" not in source, f"{path} imports human_only"
