"""Sprint 2.3 runtime, compatibility, permission and SSE acceptance tests."""

import asyncio
from dataclasses import replace
from datetime import date, datetime, timezone
import inspect
from pathlib import Path
from types import SimpleNamespace

import pytest

from app.agents.runtime.event_stream import create_agent_event_stream
from app.agents.runtime.recruitment_runner import run_hr_report_stage, run_recruitment_strategy
from app.agents.runtime.run_store import InMemoryAgentRunStore
from app.agents.shared import AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    DecisionReviewSummary,
    RecruitmentDecisionState,
    RecruitmentCandidateContext,
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
    RecruitmentRunSnapshot,
)
from app.core.config import Settings
from app.core.container import _build_application_container
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


def build_dependencies():
    settings = Settings(
        _env_file=None,
        database_url="sqlite+pysqlite:///:memory:",
        llm_enabled=False,
        rag_enabled=False,
    )
    return _build_application_container(settings).recruitment_runner_dependencies


def build_no_review_dependencies():
    class PassingDecisionReviewTool:
        def invoke(self, _goal, profile, _job_match, _interview_evaluation):
            return DecisionReviewSummary(candidate_id=profile.candidate_id, confidence=100)

    return replace(
        build_dependencies(),
        decision_review_tool=PassingDecisionReviewTool(),  # type: ignore[arg-type]
    )


def test_compatibility_and_intelligence_packages_import() -> None:
    from app.agents import graph_factory, guardrails, state, trace
    from app.agents.tools import (
        EMPLOYEE_TOOL_CONTRACTS,
        get_my_annual_leave_balance,
        get_my_monthly_attendance_summary,
        get_my_salary_details,
    )
    from app.modules.recruitment import intelligence

    graph_nodes = set(graph_factory.build_agent_graph().get_graph().nodes)
    assert graph_nodes - {"__start__", "__end__"} == {
        "recruitment_strategy",
        "resume_parser",
        "job_match",
        "interview_evaluation",
        "decision_review",
        "hr_report",
    }
    assert set(graph_factory.RecruitmentGraphState.__annotations__) == {
        "run_id",
        "entrypoint",
        "needs_human_review",
    }
    graph_edges = {
        (edge.source, edge.target)
        for edge in graph_factory.build_agent_graph().get_graph().edges
    }
    assert graph_edges == {
        ("__start__", "recruitment_strategy"),
        ("__start__", "hr_report"),
        ("recruitment_strategy", "resume_parser"),
        ("resume_parser", "job_match"),
        ("job_match", "interview_evaluation"),
        ("interview_evaluation", "decision_review"),
        ("decision_review", "hr_report"),
        ("decision_review", "__end__"),
        ("hr_report", "__end__"),
    }
    assert "_run_recruitment_pipeline" not in inspect.getsource(graph_factory)
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

        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            build_dependencies(),
        )
        record = await store.get_owned(snapshot.run_id, 7)

        event_types = [event.event_type for event in record.events]
        assert event_types[0] is AgentEventType.WORKFLOW_STARTED
        assert AgentEventType.PLAN_CREATED in event_types
        assert AgentEventType.KNOWLEDGE_RETRIEVED in event_types
        assert event_types.count(AgentEventType.CANDIDATE_COMPLETED) == 2
        assert event_types[-1] is AgentEventType.AGENT_COMPLETED
        assert record.snapshot.status is AgentRunStatus.RUNNING
        assert record.snapshot.nodes["recruitment_strategy"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["resume_parser"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["job_match"] is AgentNodeStatus.COMPLETED
        assert record.snapshot.nodes["interview_evaluation"] is AgentNodeStatus.SKIPPED
        assert record.snapshot.nodes["decision_review"] is AgentNodeStatus.NEEDS_REVIEW
        assert record.snapshot.nodes["hr_report"] is AgentNodeStatus.WAITING
        thinking = next(event for event in record.events if event.event_type is AgentEventType.AGENT_THINKING)
        assert "optional_salary_budget" not in thinking.summary["current_goal"]
        assert {event.tool_name for event in record.events if event.tool_name} == {
            "retrieve_enterprise_knowledge",
            "extract_candidate_profile",
            "evaluate_candidate",
            "review_candidate_decision",
        }
        assert record.snapshot.completed_candidates == 2
        assert len(record.snapshot.candidate_profiles) == 2
        assert len(record.snapshot.job_matches) == 2
        assert record.snapshot.interview_evaluations == {}
        assert len(record.snapshot.decision_reviews) == 2
        assert record.snapshot.report is None
        assert all(
            any(finding.code == "INTERVIEW_DATA_MISSING" for finding in review.findings)
            for review in record.snapshot.decision_reviews.values()
        )
        assert record.snapshot.knowledge_summary is not None
        assert record.snapshot.knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
        assert record.snapshot.sources
        serialized_snapshot = record.snapshot.model_dump_json()
        assert state.context.candidates[0].resume_excerpt not in serialized_snapshot
        assert state.context.candidates[1].resume_excerpt not in serialized_snapshot

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
        assert not any(event.node_name == "hr_report" for event in record.events)

    asyncio.run(scenario())


def test_no_review_graph_runs_all_six_nodes_and_completes() -> None:
    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("no-review-run")
        dependencies = build_no_review_dependencies()
        await store.create(7, state, snapshot)

        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            dependencies,
        )
        record = await store.get(snapshot.run_id)

        assert record.snapshot.status is AgentRunStatus.COMPLETED
        assert record.snapshot.report is not None
        assert record.snapshot.nodes == {
            "recruitment_strategy": AgentNodeStatus.COMPLETED,
            "resume_parser": AgentNodeStatus.COMPLETED,
            "job_match": AgentNodeStatus.COMPLETED,
            "interview_evaluation": AgentNodeStatus.SKIPPED,
            "decision_review": AgentNodeStatus.COMPLETED,
            "hr_report": AgentNodeStatus.COMPLETED,
        }
        completed_projection = [
            (
                event.event_type,
                event.agent_name,
                event.node_name,
                event.status,
                event.display_name,
                event.candidate_id,
                event.tool_name,
            )
            for event in record.events
            if event.event_type is AgentEventType.AGENT_COMPLETED
        ]
        assert completed_projection == [
            (AgentEventType.AGENT_COMPLETED, "recruitment_strategy", "recruitment_strategy", AgentNodeStatus.COMPLETED, "招聘策略 Agent 已完成", None, None),
            (AgentEventType.AGENT_COMPLETED, "resume_parser", "resume_parser", AgentNodeStatus.COMPLETED, "简历解析 Agent 已完成", None, None),
            (AgentEventType.AGENT_COMPLETED, "job_match", "job_match", AgentNodeStatus.COMPLETED, "岗位匹配 Agent 已完成", None, None),
            (AgentEventType.AGENT_COMPLETED, "interview_evaluation", "interview_evaluation", AgentNodeStatus.SKIPPED, "面试评估 Agent 已跳过", None, None),
            (AgentEventType.AGENT_COMPLETED, "decision_review", "decision_review", AgentNodeStatus.COMPLETED, "决策审查 Agent 已完成", None, None),
            (AgentEventType.AGENT_COMPLETED, "hr_report", "hr_report", AgentNodeStatus.COMPLETED, "HR 最终报告节点已完成", None, None),
        ]
        interview_event = next(
            event for event in record.events if event.node_name == "interview_evaluation"
        )
        assert interview_event.status is AgentNodeStatus.SKIPPED
        assert interview_event.summary["skip_reason"] == (
            "STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE"
        )
        assert record.events[-1].event_type is AgentEventType.WORKFLOW_COMPLETED

    asyncio.run(scenario())


def test_job_match_review_still_runs_interview_and_decision_then_report_after_approval() -> None:
    class ReviewRequiredEvaluationTool:
        def __init__(self, delegate) -> None:
            self.delegate = delegate

        def invoke(self, *args, **kwargs):
            result = self.delegate.invoke(*args, **kwargs)
            return result.model_copy(update={"requires_review": True})

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("job-match-review-run")
        dependencies = build_no_review_dependencies()
        dependencies = replace(
            dependencies,
            candidate_evaluation_tool=ReviewRequiredEvaluationTool(
                dependencies.candidate_evaluation_tool
            ),  # type: ignore[arg-type]
        )
        await store.create(7, state, snapshot)

        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            dependencies,
        )
        waiting = await store.get(snapshot.run_id)
        assert waiting.snapshot.nodes["job_match"] is AgentNodeStatus.NEEDS_REVIEW
        assert waiting.snapshot.nodes["interview_evaluation"] is AgentNodeStatus.SKIPPED
        assert waiting.snapshot.nodes["decision_review"] is AgentNodeStatus.COMPLETED
        assert waiting.snapshot.nodes["hr_report"] is AgentNodeStatus.WAITING
        assert waiting.snapshot.report is None

        waiting.snapshot.nodes["job_match"] = AgentNodeStatus.COMPLETED
        waiting.state.node_statuses["job_match"] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(snapshot.run_id, waiting.snapshot, waiting.state)
        await run_hr_report_stage(snapshot.run_id, store, dependencies)
        await run_hr_report_stage(snapshot.run_id, store, dependencies)

        completed = await store.get(snapshot.run_id)
        assert completed.snapshot.status is AgentRunStatus.COMPLETED
        assert completed.snapshot.report is not None
        assert sum(
            event.event_type is AgentEventType.REPORT_GENERATED
            for event in completed.events
        ) == 1

    asyncio.run(scenario())


def test_tool_failure_marks_one_node_and_publishes_one_failure() -> None:
    class FailingProfileTool:
        def invoke(self, _candidate):
            raise RuntimeError("sensitive tool failure")

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("tool-failure-run")
        dependencies = replace(
            build_dependencies(),
            profile_tool=FailingProfileTool(),  # type: ignore[arg-type]
        )
        await store.create(7, state, snapshot)
        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            dependencies,
        )

        record = await store.get(snapshot.run_id)
        failure_events = [
            event
            for event in record.events
            if event.event_type is AgentEventType.WORKFLOW_FAILED
        ]
        assert record.snapshot.status is AgentRunStatus.FAILED
        assert record.snapshot.nodes["resume_parser"] is AgentNodeStatus.FAILED
        assert len(failure_events) == 1
        assert failure_events[0].summary["failed_node"] == "resume_parser"
        assert failure_events[0].summary["failed_step"] == "extract_candidate_profile"
        assert failure_events[0].candidate_id == 101
        assert "sensitive tool failure" not in failure_events[0].model_dump_json()

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


def test_existing_decision_review_endpoint_keeps_approval_and_duplicate_contract(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    from app.api.v1.endpoints import agent
    from app.modules.auth.models import User

    scheduled: list[str] = []
    monkeypatch.setattr(
        agent,
        "schedule_hr_report_stage",
        lambda run_id, _store, _dependencies: scheduled.append(run_id),
    )

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("decision-approval-run")
        dependencies = build_dependencies()
        await store.create(7, state, snapshot)
        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            dependencies,
        )
        user = User(
            id=7,
            username="hr",
            password_hash="x",
            role="HR_SPECIALIST",
            permissions=["agent.hr.use"],
        )
        container = SimpleNamespace(
            agent_run_store=store,
            recruitment_runner_dependencies=dependencies,
        )

        response = await agent.approve_decision_review(
            snapshot.run_id,
            user,
            container,  # type: ignore[arg-type]
        )
        assert response.data is not None
        assert response.data.nodes["decision_review"] is AgentNodeStatus.COMPLETED
        assert scheduled == [snapshot.run_id]

        with pytest.raises(TalentFlowError) as exc_info:
            await agent.approve_decision_review(
                snapshot.run_id,
                user,
                container,  # type: ignore[arg-type]
            )
        assert exc_info.value.code == "RECRUITMENT_REVIEW_NOT_PENDING"
        assert exc_info.value.status_code == 409

    asyncio.run(scenario())

    route_paths = {route.path for route in agent.router.routes}
    assert "/recruitment/runs/{run_id}/approve-job-match-review" in route_paths
    assert "/recruitment/runs/{run_id}/approve-decision-review" in route_paths


def test_sse_replays_history_and_closes_after_terminal_event() -> None:
    class ConnectedRequest:
        async def is_disconnected(self) -> bool:
            return False

    async def scenario() -> list[str]:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("sse-run")
        await store.create(7, state, snapshot)
        await run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            build_no_review_dependencies(),
        )
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

    from app.agents.workflows.recruitment_decision import strategy_agent

    monkeypatch.setattr(strategy_agent, "build_recruitment_execution_plan", fail_plan)

    async def scenario() -> None:
        store = InMemoryAgentRunStore()
        state, snapshot = build_models("failed-run")
        await store.create(7, state, snapshot)
        await recruitment_runner.run_recruitment_strategy(
            snapshot.run_id,
            state.context,
            store,
            build_dependencies(),
        )
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
