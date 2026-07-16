"""Auditable recruitment runtime with deterministic core and optional model enhancement."""

import asyncio
from datetime import datetime, timezone
from time import perf_counter
from uuid import uuid4

from app.agents.runtime.run_store import AgentRunStore
from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.shared import AgentErrorInfo, AgentEvent, AgentEventType, AgentNodeStatus, AgentRunStatus
from app.agents.workflows.recruitment_decision.contracts import (
    DecisionReviewSummary,
    RecruitmentRunContext,
)
from app.agents.workflows.recruitment_decision.decision_review_agent import run_decision_review
from app.agents.workflows.recruitment_decision.graph import RECRUITMENT_WORKFLOW_NODES
from app.agents.workflows.recruitment_decision.job_match_agent import run_job_match
from app.agents.workflows.recruitment_decision.report_agent import build_hr_report, enhance_hr_report
from app.agents.workflows.recruitment_decision.strategy_agent import (
    build_recruitment_execution_plan,
    enhance_recruitment_execution_plan,
)

STRATEGY_NODE = "recruitment_strategy"
RESUME_NODE = "resume_parser"
JOB_MATCH_NODE = "job_match"
INTERVIEW_NODE = "interview_evaluation"
DECISION_REVIEW_NODE = "decision_review"
REPORT_NODE = "hr_report"
INTERVIEW_SKIP_REASON = "STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE"
RUN_SCOPE = "SPRINT_2_3_INTEGRATED"
NEXT_PHASE = "END_TO_END_VALIDATION"
KNOWLEDGE_TOOL_NAME = "retrieve_enterprise_knowledge"
RESUME_TOOL_NAME = "extract_candidate_profile"
JOB_MATCH_TOOL_NAME = "evaluate_candidate"
DECISION_REVIEW_TOOL_NAME = "review_candidate_decision"
REPORT_TOOL_NAME = "build_recruitment_report"
_RUNNING_TASKS: set[asyncio.Task[None]] = set()


def schedule_recruitment_strategy_run(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    resolved_store = store or _default_store()
    resolved = dependencies or _default_dependencies()
    task = asyncio.create_task(run_recruitment_strategy(run_id, context, resolved_store, resolved))
    _RUNNING_TASKS.add(task)
    task.add_done_callback(_RUNNING_TASKS.discard)


async def run_recruitment_strategy(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    from app.agents.graph_factory import build_agent_graph

    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    graph = build_agent_graph()
    await graph.ainvoke(
        {
            "run_id": run_id,
            "context": context,
            "store": resolved_store,
            "dependencies": resolved_dependencies,
            "runnable": False,
            "completed": False,
        }
    )


async def _run_recruitment_pipeline(
    run_id: str,
    context: RecruitmentRunContext,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> None:
    record = await store.get(run_id)
    snapshot = record.snapshot
    state = record.state
    started_at = perf_counter()
    knowledge_fallback_used = False
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
            "招聘决策工作流已启动",
            {
                "current_scope": RUN_SCOPE,
                "job_id": context.job.job_id,
                "candidate_count": len(context.candidate_ids),
                "orchestration_engine": "langgraph",
                "graph_name": "recruitment_decision",
            },
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
        current_step = "retrieve_enterprise_knowledge"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
            "开始读取企业招聘知识",
            {"current_action": "与招聘策略叙述增强并行检索当前岗位知识"},
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE, tool_name=KNOWLEDGE_TOOL_NAME,
        ))
        current_step = "enhance_strategy_and_retrieve_enterprise_knowledge"
        plan, knowledge_result = await asyncio.gather(
            enhance_recruitment_execution_plan(
                plan,
                context.job,
                dependencies.model_gateway,
                timeout_seconds=dependencies.strategy_model_timeout_seconds,
                max_completion_tokens=dependencies.strategy_max_completion_tokens,
            ),
            dependencies.knowledge_tool.invoke(context),
        )
        knowledge_summary, job_rubric = knowledge_result
        knowledge_fallback_used = knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
        state.execution_plan = plan
        snapshot.execution_plan = plan
        state.knowledge_summary = knowledge_summary
        state.job_rubric = job_rubric
        state.sources = knowledge_summary.sources
        snapshot.knowledge_summary = knowledge_summary
        snapshot.job_rubric = job_rubric
        snapshot.sources = knowledge_summary.sources
        await store.update_snapshot(run_id, snapshot, state)
        current_step = "publish_plan_created"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.PLAN_CREATED, AgentNodeStatus.RUNNING,
            "招聘策略执行计划已生成",
            {
                "execution_plan": plan.model_dump(mode="json"),
                "generation_mode": plan.generation_mode,
                "model_name": plan.model_name,
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
            duration_ms=plan.model_duration_ms, fallback_used=plan.fallback_used,
        ))
        current_step = "publish_enterprise_knowledge"
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
            "企业招聘知识读取完成",
            {
                "retrieval_mode": knowledge_summary.retrieval_mode,
                "standard_version": knowledge_summary.standard_version,
                "source_count": len(knowledge_summary.sources),
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE, tool_name=KNOWLEDGE_TOOL_NAME,
            source_count=len(knowledge_summary.sources), fallback_used=knowledge_fallback_used,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.KNOWLEDGE_RETRIEVED, AgentNodeStatus.RUNNING,
            "企业岗位知识已检索",
            {
                "knowledge_summary": knowledge_summary.model_dump(mode="json"),
                "job_rubric": job_rubric.model_dump(mode="json"),
            },
            agent_name=STRATEGY_NODE, node_name=STRATEGY_NODE,
            source_count=len(knowledge_summary.sources), fallback_used=knowledge_fallback_used,
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
            source_count=len(knowledge_summary.sources), duration_ms=_elapsed_ms(started_at),
            fallback_used=knowledge_fallback_used or plan.fallback_used,
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
            "简历解析 Agent 正在准备确定性事实提取",
            {
                "current_goal": "提取白名单事实、缺失项和可定位证据",
                "candidate_count": len(context.candidates),
                "missing_information": ["简历解析节点不使用 LLM，仅读取现有白名单字段"],
                "next_action": "逐名调用简历画像 Tool",
            },
            agent_name=RESUME_NODE, node_name=RESUME_NODE, fallback_used=True,
        ))

        profile_tool = dependencies.profile_tool
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

        if state.job_rubric is None or state.knowledge_summary is None:
            raise RuntimeError("recruitment knowledge context is unavailable")

        current_node = JOB_MATCH_NODE
        current_step = "start_job_match"
        job_match_started_at = perf_counter()
        snapshot.current_agent = JOB_MATCH_NODE
        snapshot.current_node = JOB_MATCH_NODE
        snapshot.nodes[JOB_MATCH_NODE] = AgentNodeStatus.RUNNING
        state.current_agent = JOB_MATCH_NODE
        state.current_node = JOB_MATCH_NODE
        state.node_statuses[JOB_MATCH_NODE] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "岗位匹配 Agent 已启动",
            {"current_action": "逐名调用确定性候选人评估 Tool", "candidate_count": len(context.candidate_ids)},
            agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "岗位匹配 Agent 正在准备确定性评分",
            {
                "current_goal": "保留人工维护评分结果并汇总技能缺口与证据",
                "candidate_count": len(context.candidate_ids),
                "scoring_mode": "DETERMINISTIC_HUMAN_ONLY",
                "next_action": "逐名调用候选人评估 Tool",
            },
            agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE,
        ))

        evaluation_tool = dependencies.candidate_evaluation_tool
        job_match_requires_review = False
        for candidate_id in context.candidate_ids:
            candidate_started_at = perf_counter()
            current_step = "evaluate_candidate"
            snapshot.current_candidate_id = candidate_id
            state.current_candidate_id = candidate_id
            await store.update_snapshot(run_id, snapshot, state)
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
                f"开始评估候选人 #{candidate_id} 的岗位匹配",
                {"current_action": "调用确定性评分边界并校验证据引用"},
                agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE, candidate_id=candidate_id,
                tool_name=JOB_MATCH_TOOL_NAME,
            ))
            job_match = run_job_match(
                context,
                state.candidate_profiles[candidate_id],
                state.job_rubric,
                state.knowledge_summary,
                evaluation_tool,
            )
            state.job_matches[candidate_id] = job_match
            snapshot.job_matches[candidate_id] = job_match
            candidate_needs_review = (
                job_match.requires_review
                or job_match.overall_score is None
                or job_match.job_match_score is None
            )
            job_match_requires_review = job_match_requires_review or candidate_needs_review
            await store.update_snapshot(run_id, snapshot, state)
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 岗位匹配评估完成",
                {
                    "candidate_id": candidate_id,
                    "overall_score": job_match.overall_score,
                    "job_match_score": job_match.job_match_score,
                    "requires_review": candidate_needs_review,
                },
                agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE, candidate_id=candidate_id,
                tool_name=JOB_MATCH_TOOL_NAME, duration_ms=_elapsed_ms(candidate_started_at),
            ))
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.INTERMEDIATE_RESULT, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 岗位匹配结果已生成",
                {"job_match_summary": job_match.model_dump(mode="json")},
                agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE, candidate_id=candidate_id,
                source_count=len(job_match.knowledge_sources),
            ))

        current_step = "complete_job_match"
        snapshot.current_candidate_id = None
        state.current_candidate_id = None
        job_match_status = (
            AgentNodeStatus.NEEDS_REVIEW if job_match_requires_review else AgentNodeStatus.COMPLETED
        )
        snapshot.nodes[JOB_MATCH_NODE] = job_match_status
        state.node_statuses[JOB_MATCH_NODE] = job_match_status
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, job_match_status,
            "岗位匹配 Agent 已完成，存在结果需人工复核"
            if job_match_requires_review else "岗位匹配 Agent 已完成",
            {
                "completed_node": JOB_MATCH_NODE,
                "evaluated_candidates": len(state.job_matches),
                "review_required": job_match_requires_review,
                "next_action": "跳过无真实数据的面试评估并执行决策审查",
            },
            agent_name=JOB_MATCH_NODE, node_name=JOB_MATCH_NODE,
            source_count=len(snapshot.sources), duration_ms=_elapsed_ms(job_match_started_at),
        ))

        current_node = INTERVIEW_NODE
        current_step = "skip_interview_evaluation"
        snapshot.current_agent = INTERVIEW_NODE
        snapshot.current_node = INTERVIEW_NODE
        snapshot.nodes[INTERVIEW_NODE] = AgentNodeStatus.SKIPPED
        state.current_agent = INTERVIEW_NODE
        state.current_node = INTERVIEW_NODE
        state.node_statuses[INTERVIEW_NODE] = AgentNodeStatus.SKIPPED
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.SKIPPED,
            "面试评估 Agent 已跳过",
            {
                "skip_reason": INTERVIEW_SKIP_REASON,
                "structured_interview_feedback_available": False,
                "interview_conclusion_generated": False,
                "next_action": "决策审查将缺少真实面试评价标记为待人工补充",
            },
            agent_name=INTERVIEW_NODE, node_name=INTERVIEW_NODE,
        ))

        current_node = DECISION_REVIEW_NODE
        current_step = "start_decision_review"
        review_started_at = perf_counter()
        snapshot.current_agent = DECISION_REVIEW_NODE
        snapshot.current_node = DECISION_REVIEW_NODE
        snapshot.nodes[DECISION_REVIEW_NODE] = AgentNodeStatus.RUNNING
        state.current_agent = DECISION_REVIEW_NODE
        state.current_node = DECISION_REVIEW_NODE
        state.node_statuses[DECISION_REVIEW_NODE] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "决策审查 Agent 已启动",
            {"current_action": "逐名检查评分、必备条件、证据、画像完整度和面试缺失"},
            agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "决策审查 Agent 正在准备规则审查",
            {
                "current_goal": "用公开确定性公式计算可信度并保留原始评分",
                "candidate_count": len(context.candidate_ids),
                "interview_data_status": INTERVIEW_SKIP_REASON,
                "next_action": "逐名调用决策审查 Tool",
            },
            agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
        ))

        review_tool = dependencies.decision_review_tool
        decision_requires_review = False
        for candidate_id in context.candidate_ids:
            candidate_started_at = perf_counter()
            current_step = "review_candidate_decision"
            snapshot.current_candidate_id = candidate_id
            state.current_candidate_id = candidate_id
            await store.update_snapshot(run_id, snapshot, state)
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
                f"开始审查候选人 #{candidate_id} 的决策依据",
                {"current_action": "执行规则式证据、阈值和风险审查"},
                agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
                candidate_id=candidate_id, tool_name=DECISION_REVIEW_TOOL_NAME,
            ))
            review = run_decision_review(
                context.request.goal,
                state.candidate_profiles[candidate_id],
                state.job_matches[candidate_id],
                state.interview_evaluations.get(candidate_id),
                review_tool,
            )
            state.decision_reviews[candidate_id] = review
            snapshot.decision_reviews[candidate_id] = review
            candidate_needs_review = _decision_requires_review(
                review,
                context.request.goal.confidence_threshold,
            )
            decision_requires_review = decision_requires_review or candidate_needs_review
            await store.update_snapshot(run_id, snapshot, state)
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 决策审查完成",
                {
                    "candidate_id": candidate_id,
                    "confidence": review.confidence,
                    "finding_count": len(review.findings),
                    "requires_review": candidate_needs_review,
                },
                agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
                candidate_id=candidate_id, tool_name=DECISION_REVIEW_TOOL_NAME,
                duration_ms=_elapsed_ms(candidate_started_at),
            ))
            await _publish(store, _event(
                run_id, snapshot.trace_id, AgentEventType.REVIEW_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 审查结果已生成",
                {"decision_review": review.model_dump(mode="json")},
                agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
                candidate_id=candidate_id,
            ))

        current_step = "complete_decision_review"
        snapshot.current_candidate_id = None
        state.current_candidate_id = None
        review_status = (
            AgentNodeStatus.NEEDS_REVIEW if decision_requires_review else AgentNodeStatus.COMPLETED
        )
        snapshot.nodes[DECISION_REVIEW_NODE] = review_status
        state.node_statuses[DECISION_REVIEW_NODE] = review_status
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, review_status,
            "决策审查 Agent 已完成，结果需 HR 复核"
            if decision_requires_review else "决策审查 Agent 已完成",
            {
                "completed_node": DECISION_REVIEW_NODE,
                "reviewed_candidates": len(state.decision_reviews),
                "review_required": decision_requires_review,
                "deterministic_scores_preserved": all(
                    review.deterministic_score_preserved for review in state.decision_reviews.values()
                ),
                "next_action": "等待 HR 审查通过后生成 HR 最终报告"
                if job_match_status is AgentNodeStatus.NEEDS_REVIEW
                or review_status is AgentNodeStatus.NEEDS_REVIEW
                else "生成 HR 结构化最终报告",
            },
            agent_name=DECISION_REVIEW_NODE, node_name=DECISION_REVIEW_NODE,
            duration_ms=_elapsed_ms(review_started_at),
        ))

        if (
            job_match_status is AgentNodeStatus.NEEDS_REVIEW
            or review_status is AgentNodeStatus.NEEDS_REVIEW
        ):
            snapshot.status = AgentRunStatus.RUNNING
            snapshot.current_agent = None
            snapshot.current_node = None
            snapshot.current_candidate_id = None
            state.status = AgentRunStatus.RUNNING
            state.current_agent = None
            state.current_node = None
            state.current_candidate_id = None
            await store.update_snapshot(run_id, snapshot, state)
            return

        await run_hr_report_stage(run_id, store, dependencies)
    except Exception:
        error = AgentErrorInfo(
            code="RECRUITMENT_WORKFLOW_FAILED",
            message="招聘决策工作流执行失败。",
            details={
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
            "招聘决策工作流失败",
            {"failed_node": current_node, "failed_step": current_step, "current_scope": RUN_SCOPE},
            agent_name=current_node, node_name=current_node, candidate_id=snapshot.current_candidate_id,
            duration_ms=_elapsed_ms(started_at), fallback_used=knowledge_fallback_used, error=error,
        ))


def schedule_hr_report_stage(
    run_id: str,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    """Schedule one persisted Run's HR report stage after HR approval."""

    resolved_store = store or _default_store()
    resolved_dependencies = dependencies or _default_dependencies()
    task = asyncio.create_task(run_hr_report_stage(run_id, resolved_store, resolved_dependencies))
    _RUNNING_TASKS.add(task)
    task.add_done_callback(_RUNNING_TASKS.discard)


async def run_hr_report_stage(
    run_id: str,
    store: AgentRunStore | None = None,
    dependencies: RecruitmentRunnerDependencies | None = None,
) -> None:
    """Generate the report from the newest persisted state exactly once per stage start."""

    store = store or _default_store()
    dependencies = dependencies or _default_dependencies()
    record = await store.get(run_id)
    snapshot = record.snapshot
    state = record.state
    context = state.context
    plan = state.execution_plan
    started_at = perf_counter()
    current_node = REPORT_NODE
    current_step = "validate_hr_report_stage"
    knowledge_fallback_used = (
        state.knowledge_summary is not None
        and state.knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
    )
    try:
        if (
            snapshot.status is not AgentRunStatus.RUNNING
            or snapshot.report is not None
            or snapshot.nodes.get(REPORT_NODE) is not AgentNodeStatus.WAITING
            or snapshot.nodes.get(JOB_MATCH_NODE) is AgentNodeStatus.NEEDS_REVIEW
            or snapshot.nodes.get(DECISION_REVIEW_NODE) is AgentNodeStatus.NEEDS_REVIEW
        ):
            return
        if plan is None or state.knowledge_summary is None:
            raise RuntimeError("recruitment report context is unavailable")

        current_step = "start_hr_report"
        snapshot.status = AgentRunStatus.RUNNING
        snapshot.current_agent = REPORT_NODE
        snapshot.current_node = REPORT_NODE
        snapshot.current_candidate_id = None
        snapshot.nodes[REPORT_NODE] = AgentNodeStatus.RUNNING
        state.status = AgentRunStatus.RUNNING
        state.current_agent = REPORT_NODE
        state.current_node = REPORT_NODE
        state.current_candidate_id = None
        state.node_statuses[REPORT_NODE] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "HR 最终报告节点已启动",
            {"current_action": "汇总真实评分、审查结果、知识来源和人才缺口"},
            agent_name=REPORT_NODE, node_name=REPORT_NODE,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "HR 最终报告节点正在准备结构化汇总",
            {
                "current_goal": "先生成确定性报告，再按配置增强允许的叙述字段",
                "candidate_count": len(context.candidate_ids),
                "next_action": "调用招聘报告 Tool",
            },
            agent_name=REPORT_NODE, node_name=REPORT_NODE,
        ))
        report_tool = dependencies.report_tool
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
            "开始生成 HR 结构化报告",
            {"current_action": "执行稳定排序、来源去重和人才缺口汇总"},
            agent_name=REPORT_NODE, node_name=REPORT_NODE, tool_name=REPORT_TOOL_NAME,
        ))
        current_step = "build_hr_report"
        report = build_hr_report(
            context.request.goal,
            state.job_matches,
            state.decision_reviews,
            state.knowledge_summary,
            state.candidate_profiles,
            state.interview_evaluations,
            report_tool,
        )
        report = await enhance_hr_report(
            report,
            dependencies.model_gateway,
            timeout_seconds=dependencies.report_model_timeout_seconds,
            max_completion_tokens=dependencies.report_max_completion_tokens,
        )
        state.report = report
        snapshot.report = report
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
            "HR 结构化报告生成完成",
            {
                "candidate_count": len(report.candidate_rankings),
                "knowledge_source_count": len(report.knowledge_sources),
                "requires_human_decision": report.requires_human_decision,
                "generation_mode": report.generation_mode,
                "model_name": report.model_name,
            },
            agent_name=REPORT_NODE, node_name=REPORT_NODE, tool_name=REPORT_TOOL_NAME,
            source_count=len(report.knowledge_sources), duration_ms=_elapsed_ms(started_at),
            fallback_used=report.fallback_used,
        ))
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.REPORT_GENERATED, AgentNodeStatus.RUNNING,
            "HR 最终报告已生成",
            {"report": report.model_dump(mode="json")},
            agent_name=REPORT_NODE, node_name=REPORT_NODE,
            source_count=len(report.knowledge_sources), duration_ms=report.model_duration_ms,
            fallback_used=report.fallback_used,
        ))
        snapshot.nodes[REPORT_NODE] = AgentNodeStatus.COMPLETED
        state.node_statuses[REPORT_NODE] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(run_id, snapshot, state)
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.COMPLETED,
            "HR 最终报告节点已完成",
            {
                "completed_node": REPORT_NODE,
                "report_generated": True,
                "requires_human_decision": report.requires_human_decision,
                "generation_mode": report.generation_mode,
                "model_name": report.model_name,
                "next_action": "由 HR 查看报告并完成人工决定",
            },
            agent_name=REPORT_NODE, node_name=REPORT_NODE,
            source_count=len(report.knowledge_sources), duration_ms=_elapsed_ms(started_at),
            fallback_used=report.fallback_used,
        ))

        current_step = "complete_workflow"
        snapshot.status = AgentRunStatus.COMPLETED
        snapshot.current_agent = None
        snapshot.current_node = None
        snapshot.current_candidate_id = None
        state.status = AgentRunStatus.COMPLETED
        state.current_agent = None
        state.current_node = None
        state.current_candidate_id = None
        await store.update_snapshot(run_id, snapshot, state)
        review_required_candidates = sum(
            _decision_requires_review(review, context.request.goal.confidence_threshold)
            for review in state.decision_reviews.values()
        )
        await _publish(store, _event(
            run_id, snapshot.trace_id, AgentEventType.WORKFLOW_COMPLETED, AgentNodeStatus.COMPLETED,
            "招聘决策工作流已完成",
            {
                "current_scope": RUN_SCOPE,
                "executed_nodes": plan.executed_nodes,
                "skipped_nodes": plan.skipped_nodes,
                "skip_reasons": {INTERVIEW_NODE: INTERVIEW_SKIP_REASON},
                "total_candidates": snapshot.total_candidates,
                "scored_candidates": sum(
                    match.overall_score is not None and match.job_match_score is not None
                    for match in state.job_matches.values()
                ),
                "review_required_candidates": review_required_candidates,
                "knowledge_source_count": len(snapshot.sources),
                "report_generated": snapshot.report is not None,
                "next_phase": NEXT_PHASE,
            },
            source_count=len(snapshot.sources), duration_ms=_elapsed_ms(started_at),
            fallback_used=knowledge_fallback_used or plan.fallback_used or report.fallback_used,
        ))
    except Exception:
        error = AgentErrorInfo(
            code="RECRUITMENT_WORKFLOW_FAILED",
            message="招聘决策工作流执行失败。",
            details={"failed_node": current_node, "failed_step": current_step},
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
            "招聘决策工作流失败",
            {"failed_node": current_node, "failed_step": current_step, "current_scope": RUN_SCOPE},
            agent_name=current_node, node_name=current_node,
            duration_ms=_elapsed_ms(started_at), fallback_used=knowledge_fallback_used, error=error,
        ))


def _decision_requires_review(
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


async def _publish(store: AgentRunStore, event: AgentEvent) -> None:
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


def _default_dependencies() -> RecruitmentRunnerDependencies:
    from app.core.container import get_application_container

    return get_application_container().recruitment_runner_dependencies


def _default_store() -> AgentRunStore:
    from app.core.container import get_application_container

    return get_application_container().agent_run_store
