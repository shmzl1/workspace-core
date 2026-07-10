"""Real Sprint 2.1 strategy runner without LangGraph, LLM, RAG or database access."""

import asyncio
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.agents.runtime.run_store import InMemoryAgentRunStore, agent_run_store
from app.agents.shared import AgentErrorInfo, AgentEvent, AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import RecruitmentRunContext
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.agents.workflows.recruitment_decision.strategy_agent import build_recruitment_execution_plan

STRATEGY_NODE = "recruitment_strategy"
SKIP_REASON = "CURRENT_PHASE_NOT_IMPLEMENTED"
RUN_SCOPE = "SPRINT_2_1_STRATEGY_ONLY"
NEXT_PHASE = "SPRINT_2_2"
_RUNNING_TASKS: set[asyncio.Task[None]] = set()


def schedule_recruitment_strategy_run(
    run_id: str,
    context: RecruitmentRunContext,
    store: InMemoryAgentRunStore = agent_run_store,
) -> None:
    task = asyncio.create_task(run_recruitment_strategy(run_id, context, store))
    _RUNNING_TASKS.add(task)
    task.add_done_callback(_RUNNING_TASKS.discard)


async def run_recruitment_strategy(
    run_id: str,
    context: RecruitmentRunContext,
    store: InMemoryAgentRunStore = agent_run_store,
) -> None:
    record = await store.get(run_id)
    snapshot = record.snapshot
    state = record.state
    started_at = perf_counter()
    try:
        snapshot.status = AgentRunStatus.RUNNING
        snapshot.current_agent = STRATEGY_NODE
        snapshot.current_node = STRATEGY_NODE
        snapshot.nodes[STRATEGY_NODE] = AgentNodeStatus.RUNNING
        state.status = AgentRunStatus.RUNNING
        state.current_agent = STRATEGY_NODE
        state.current_node = STRATEGY_NODE
        state.node_statuses[STRATEGY_NODE] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)

        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.WORKFLOW_STARTED,
                AgentNodeStatus.RUNNING,
                "招聘策略规划工作流已启动",
                {
                    "current_scope": RUN_SCOPE,
                    "job_id": context.job.job_id,
                    "candidate_count": len(context.candidate_ids),
                },
            ),
        )
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.AGENT_STARTED,
                AgentNodeStatus.RUNNING,
                "招聘策略 Agent 已启动",
                {"current_action": "读取已校验的企业招聘目标和静态工作流结构"},
            ),
        )
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.AGENT_THINKING,
                AgentNodeStatus.RUNNING,
                "招聘策略 Agent 正在规划",
                {
                    "current_goal": context.request.goal.model_dump(mode="json"),
                    "candidate_count": len(context.candidate_ids),
                    "current_action": "生成结构化执行计划",
                    "missing_information": ["后续专业 Agent 所需分析结果尚未生成"],
                    "next_action": "确定当前执行节点和后续跳过节点",
                },
            ),
        )

        plan = build_recruitment_execution_plan(
            context.request,
            context.job,
            context.candidate_ids,
            RECRUITMENT_WORKFLOW_NODES,
        )
        state.execution_plan = plan
        snapshot.execution_plan = plan
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.PLAN_CREATED,
                AgentNodeStatus.RUNNING,
                "招聘策略执行计划已生成",
                {"execution_plan": plan.model_dump(mode="json")},
            ),
        )

        strategy_duration_ms = _elapsed_ms(started_at)
        snapshot.nodes[STRATEGY_NODE] = AgentNodeStatus.COMPLETED
        state.node_statuses[STRATEGY_NODE] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.AGENT_COMPLETED,
                AgentNodeStatus.COMPLETED,
                "招聘策略 Agent 已完成",
                {"completed_node": STRATEGY_NODE, "plan_created": True},
                duration_ms=strategy_duration_ms,
            ),
        )

        for node_name in plan.skipped_nodes:
            snapshot.nodes[node_name] = AgentNodeStatus.SKIPPED
            state.node_statuses[node_name] = AgentNodeStatus.SKIPPED
        snapshot.status = AgentRunStatus.COMPLETED
        snapshot.current_agent = None
        snapshot.current_node = None
        state.status = AgentRunStatus.COMPLETED
        state.current_agent = None
        state.current_node = None
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.WORKFLOW_COMPLETED,
                AgentNodeStatus.COMPLETED,
                "Sprint 2.1 招聘策略规划已完成",
                {
                    "current_scope": RUN_SCOPE,
                    "skipped_nodes": plan.skipped_nodes,
                    "skip_reason": SKIP_REASON,
                    "next_phase": NEXT_PHASE,
                },
                duration_ms=_elapsed_ms(started_at),
            ),
        )
    except Exception as exc:
        error = AgentErrorInfo(
            code="RECRUITMENT_STRATEGY_FAILED",
            message="招聘策略规划执行失败。",
            details={"exception_type": type(exc).__name__},
        )
        snapshot.status = AgentRunStatus.FAILED
        snapshot.current_agent = STRATEGY_NODE
        snapshot.current_node = STRATEGY_NODE
        snapshot.nodes[STRATEGY_NODE] = AgentNodeStatus.FAILED
        snapshot.error = error
        state.status = AgentRunStatus.FAILED
        state.current_agent = STRATEGY_NODE
        state.current_node = STRATEGY_NODE
        state.node_statuses[STRATEGY_NODE] = AgentNodeStatus.FAILED
        state.error = error
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(
            store,
            _event(
                run_id,
                snapshot.trace_id,
                AgentEventType.WORKFLOW_FAILED,
                AgentNodeStatus.FAILED,
                "招聘策略规划失败",
                {"failed_node": STRATEGY_NODE, "current_scope": RUN_SCOPE},
                duration_ms=_elapsed_ms(started_at),
                error=error,
            ),
        )


async def _publish(store: InMemoryAgentRunStore, event: AgentEvent) -> None:
    await store.append_event(event.run_id, event)


def _event(
    run_id: str,
    trace_id: str,
    event_type: AgentEventType,
    status: AgentNodeStatus,
    display_name: str,
    summary: dict[str, object],
    duration_ms: int | None = None,
    error: AgentErrorInfo | None = None,
) -> AgentEvent:
    return AgentEvent(
        event_id=uuid4().hex,
        run_id=run_id,
        trace_id=trace_id,
        agent_name=STRATEGY_NODE,
        node_name=STRATEGY_NODE,
        display_name=display_name,
        event_type=event_type,
        status=status,
        summary=summary,
        duration_ms=duration_ms,
        created_at=datetime.now(timezone.utc),
        error=error,
    )


def _elapsed_ms(started_at: float) -> int:
    return max(0, int((perf_counter() - started_at) * 1000))
