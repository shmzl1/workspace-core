"""Real Sprint 2.2 strategy, knowledge and resume-parser runtime."""

import asyncio
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.agents.runtime.run_store import InMemoryAgentRunStore, agent_run_store
from app.agents.shared import AgentErrorInfo, AgentEvent, AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.tools.knowledge_tools import EnterpriseKnowledgeTool
from app.agents.tools.recruitment_tools import CandidateProfileTool
from app.agents.workflows.recruitment_decision.contracts import RecruitmentRunContext
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.agents.workflows.recruitment_decision.strategy_agent import build_recruitment_execution_plan

STRATEGY_NODE = "recruitment_strategy"
RESUME_NODE = "resume_parser"
SKIP_REASON = "CURRENT_PHASE_NOT_IMPLEMENTED"
RUN_SCOPE = "SPRINT_2_2_STRATEGY_RESUME_KNOWLEDGE"
NEXT_PHASE = "SPRINT_2_3"
KNOWLEDGE_TOOL_NAME = "retrieve_enterprise_knowledge"
RESUME_TOOL_NAME = "extract_candidate_profile"
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
    current_step = "initialize_run"
    current_node = STRATEGY_NODE
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

        current_step = "publish_workflow_started"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.WORKFLOW_STARTED, AgentNodeStatus.RUNNING,
            "Sprint 2.2 招聘工作流已启动",
            {"current_scope": RUN_SCOPE, "job_id": context.job.job_id, "candidate_count": len(context.candidate_ids)},
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
        ))
        current_step = "publish_strategy_started"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "招聘策略 Agent 已启动",
            {"current_action": "读取企业招聘目标、候选人范围和已有面试状态"},
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
        ))
        current_step = "publish_strategy_thinking"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "招聘策略 Agent 正在规划",
            {
                "current_goal": context.request.goal.model_dump(mode="json", exclude={"optional_salary_budget"}),
                "candidate_count": len(context.candidate_ids),
                "resume_parse_required": True,
                "interview_candidate_ids": context.interview_candidate_ids,
                "current_action": "生成结构化执行计划",
                "next_action": "读取岗位知识并解析候选人简历",
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
        ))

        current_step = "build_execution_plan"
        plan = build_recruitment_execution_plan(
            context.request,
            context.job,
            context.candidate_ids,
            RECRUITMENT_WORKFLOW_NODES,
            context.interview_candidate_ids,
        )
        state.execution_plan = plan
        snapshot.execution_plan = plan
        await store.update_snapshot(run_id, snapshot, state)
        current_step = "publish_plan_created"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.PLAN_CREATED, AgentNodeStatus.RUNNING,
            "招聘策略执行计划已生成",
            {"execution_plan": plan.model_dump(mode="json")},
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
        ))

        current_step = "retrieve_enterprise_knowledge"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
            "开始读取企业招聘知识",
            {"current_action": "按岗位编号、部门、文档类型和生效日期检索当前知识"},
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE, tool_name=KNOWLEDGE_TOOL_NAME,
            fallback_used=True,
        ))
        knowledge_summary, job_rubric = EnterpriseKnowledgeTool().invoke(context)
        state.knowledge_summary = knowledge_summary
        state.job_rubric = job_rubric
        state.sources = knowledge_summary.sources
        snapshot.knowledge_summary = knowledge_summary
        snapshot.job_rubric = job_rubric
        snapshot.sources = knowledge_summary.sources
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
            "企业招聘知识读取完成",
            {
                "retrieval_mode": knowledge_summary.retrieval_mode,
                "standard_version": knowledge_summary.standard_version,
                "source_count": len(knowledge_summary.sources),
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE, tool_name=KNOWLEDGE_TOOL_NAME,
            source_count=len(knowledge_summary.sources), fallback_used=True,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.KNOWLEDGE_RETRIEVED, AgentNodeStatus.RUNNING,
            "企业岗位知识已检索",
            {
                "knowledge_summary": knowledge_summary.model_dump(mode="json"),
                "job_rubric": job_rubric.model_dump(mode="json"),
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
            source_count=len(knowledge_summary.sources), fallback_used=True,
        ))

        current_step = "complete_strategy_node"
        snapshot.nodes[STRATEGY_NODE] = AgentNodeStatus.COMPLETED
        state.node_statuses[STRATEGY_NODE] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.COMPLETED,
            "招聘策略 Agent 已完成",
            {
                "completed_node": STRATEGY_NODE,
                "plan_created": True,
                "knowledge_source_count": len(knowledge_summary.sources),
                "next_action": "执行简历解析 Agent",
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
            source_count=len(knowledge_summary.sources), duration_ms=_elapsed_ms(started_at), fallback_used=True,
        ))

        current_node = RESUME_NODE
        current_step = "start_resume_parser"
        resume_started_at = perf_counter()
        snapshot.current_agent = RESUME_NODE
        snapshot.current_node = RESUME_NODE
        snapshot.nodes[RESUME_NODE] = AgentNodeStatus.RUNNING
        state.current_agent = RESUME_NODE
        state.current_node = RESUME_NODE
        state.node_statuses[RESUME_NODE] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "简历解析 Agent 已启动",
            {"current_action": "按候选人顺序生成结构化画像", "candidate_count": len(context.candidates)},
            agent_name=RESUME_NODE, node_name=RESUME_NODE, fallback_used=True,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "简历解析 Agent 正在准备确定性回退提取",
            {
                "current_goal": "提取白名单事实、缺失项和可定位证据",
                "candidate_count": len(context.candidates),
                "missing_information": ["LLM 未接入，使用现有数据库字段进行确定性回退"],
                "next_action": "逐名调用简历画像 Tool",
            },
            agent_name=RESUME_NODE, node_name=RESUME_NODE, fallback_used=True,
        ))

        profile_tool = CandidateProfileTool()
        for candidate in context.candidates:
            candidate_started_at = perf_counter()
            current_step = "extract_candidate_profile"
            snapshot.current_candidate_id = candidate.candidate_id
            state.current_candidate_id = candidate.candidate_id
            await store.update_snapshot(run_id, snapshot, state)
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
                f"开始解析候选人 #{candidate.candidate_id}",
                {"current_action": "读取白名单结构化字段与安全简历片段"},
                agent_name=RESUME_NODE, node_name=RESUME_NODE, candidate_id=candidate.candidate_id,
                tool_name=RESUME_TOOL_NAME, fallback_used=True,
            ))
            profile = profile_tool.invoke(candidate)
            state.candidate_profiles[candidate.candidate_id] = profile
            snapshot.candidate_profiles[candidate.candidate_id] = profile
            snapshot.completed_candidates += 1
            await store.update_snapshot(run_id, snapshot, state)
            profile_summary = {
                "candidate_id": candidate.candidate_id,
                "skill_count": len(profile.skills),
                "project_count": len(profile.projects),
                "achievement_count": len(profile.measurable_achievements),
                "missing_field_count": len(profile.missing_fields),
                "evidence_count": len(profile.evidence_items),
                "extraction_mode": profile.extraction_mode,
            }
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate.candidate_id} 简历画像提取完成",
                profile_summary,
                agent_name=RESUME_NODE, node_name=RESUME_NODE, candidate_id=candidate.candidate_id,
                tool_name=RESUME_TOOL_NAME, duration_ms=_elapsed_ms(candidate_started_at), fallback_used=True,
            ))
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.INTERMEDIATE_RESULT, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate.candidate_id} 结构化画像已生成",
                {"candidate_profile": profile.model_dump(mode="json"), "profile_summary": profile_summary},
                agent_name=RESUME_NODE, node_name=RESUME_NODE, candidate_id=candidate.candidate_id,
                fallback_used=True,
            ))
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.CANDIDATE_COMPLETED, AgentNodeStatus.COMPLETED,
                f"候选人 #{candidate.candidate_id} 解析完成",
                {
                    "candidate_id": candidate.candidate_id,
                    "completed_candidates": snapshot.completed_candidates,
                    "total_candidates": snapshot.total_candidates,
                },
                agent_name=RESUME_NODE, node_name=RESUME_NODE, candidate_id=candidate.candidate_id,
                duration_ms=_elapsed_ms(candidate_started_at), fallback_used=True,
            ))

        current_step = "complete_resume_parser"
        snapshot.current_candidate_id = None
        state.current_candidate_id = None
        snapshot.nodes[RESUME_NODE] = AgentNodeStatus.COMPLETED
        state.node_statuses[RESUME_NODE] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.COMPLETED,
            "简历解析 Agent 已完成",
            {
                "completed_node": RESUME_NODE,
                "profile_count": len(snapshot.candidate_profiles),
                "evidence_count": sum(len(profile.evidence_items) for profile in snapshot.candidate_profiles.values()),
                "fallback_mode": "STRUCTURED_DATABASE_FALLBACK",
            },
            agent_name=RESUME_NODE, node_name=RESUME_NODE,
            duration_ms=_elapsed_ms(resume_started_at), fallback_used=True,
        ))

        current_step = "complete_workflow"
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
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.WORKFLOW_COMPLETED, AgentNodeStatus.COMPLETED,
            "Sprint 2.2 招聘策略、知识检索与简历解析已完成",
            {
                "current_scope": RUN_SCOPE,
                "executed_nodes": plan.executed_nodes,
                "skipped_nodes": plan.skipped_nodes,
                "skip_reason": SKIP_REASON,
                "completed_candidates": snapshot.completed_candidates,
                "knowledge_source_count": len(snapshot.sources),
                "next_phase": NEXT_PHASE,
            },
            source_count=len(snapshot.sources), duration_ms=_elapsed_ms(started_at), fallback_used=True,
        ))
    except Exception as exc:
        error = AgentErrorInfo(
            code="RECRUITMENT_WORKFLOW_FAILED",
            message="Sprint 2.2 招聘工作流执行失败。",
            details={
                "exception_type": type(exc).__name__,
                "failed_node": current_node,
                "failed_step": current_step,
                "candidate_id": snapshot.current_candidate_id,
            },
        )
        snapshot.status = AgentRunStatus.FAILED
        snapshot.current_agent = current_node
        snapshot.current_node = current_node
        snapshot.nodes[current_node] = AgentNodeStatus.FAILED
        snapshot.error = error
        state.status = AgentRunStatus.FAILED
        state.current_agent = current_node
        state.current_node = current_node
        state.node_statuses[current_node] = AgentNodeStatus.FAILED
        state.error = error
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.WORKFLOW_FAILED, AgentNodeStatus.FAILED,
            "Sprint 2.2 招聘工作流失败",
            {"failed_node": current_node, "failed_step": current_step, "current_scope": RUN_SCOPE},
            agent_name=current_node, node_name=current_node, candidate_id=snapshot.current_candidate_id,
            duration_ms=_elapsed_ms(started_at), fallback_used=True, error=error,
        ))


async def _publish(store: InMemoryAgentRunStore, event: AgentEvent) -> None:
    await store.append_event(event.run_id, event)


def _event(
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


def _elapsed_ms(started_at: float) -> int:
    return max(0, int((perf_counter() - started_at) * 1000))
