"""HR-report Tool orchestration and bounded model narrative enhancement."""

import asyncio
from collections.abc import Mapping

from pydantic import BaseModel, Field, ValidationError

from app.agents.prompts.loader import load_recruitment_prompt
from app.agents.shared import (
    AgentEventType,
    AgentNodeContract,
    AgentNodeStatus,
    AgentRunStatus,
    ModelGateway,
    ModelGatewayError,
    ModelGatewayInput,
    ModelGatewayOutputError,
)
from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.recruitment_support import (
    DECISION_REVIEW_NODE_NAME,
    INTERVIEW_NODE_NAME,
    INTERVIEW_SKIP_REASON,
    JOB_MATCH_NODE_NAME,
    NEXT_PHASE,
    REPORT_NODE_NAME,
    REPORT_TOOL_NAME,
    RUN_SCOPE,
    RecruitmentNodeExecution,
    decision_requires_review,
    elapsed_ms,
    event,
    execute_recruitment_node,
    publish,
)
from app.agents.runtime.run_store import AgentRunStore, RecruitmentRunRecord
from app.agents.tools.recruitment_tools import RecruitmentReportTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    HRReportSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)

HR_REPORT_NODE = AgentNodeContract(
    name="hr_report",
    display_name="HR 最终报告",
    responsibility="汇总企业招聘目标、候选人证据、来源、审查结果和建议动作。",
    required_inputs=(
        "goal",
        "job_matches",
        "decision_reviews",
        "knowledge_summary",
        "candidate_profiles",
        "interview_evaluations",
    ),
    dependencies=("decision_review",),
    allowed_tools=("build_recruitment_report",),
    output_fields=("report",),
    forbidden_behaviors=("把建议表述为已录用决定", "确认薪资", "伪造来源"),
)


def build_hr_report(
    goal: RecruitmentGoal,
    job_matches: dict[int, JobMatchSummary],
    decision_reviews: dict[int, DecisionReviewSummary],
    knowledge: EnterpriseKnowledgeSummary,
    candidate_profiles: dict[int, CandidateProfile],
    interview_evaluations: dict[int, InterviewEvaluationSummary],
    tool: RecruitmentReportTool,
) -> HRReportSummary:
    """Invoke the injected report Tool without composing candidate results here."""

    return tool.invoke(
        goal,
        job_matches,
        decision_reviews,
        knowledge,
        candidate_profiles,
        interview_evaluations,
    )


class HRReportEnhancement(BaseModel):
    executive_summary: str | None = None
    talent_gaps: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    risk_summary: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


async def enhance_hr_report(
    report: HRReportSummary,
    model_gateway: ModelGateway,
    *,
    timeout_seconds: float = 35.0,
    max_completion_tokens: int = 768,
) -> HRReportSummary:
    """Enhance narrative fields without changing rankings, reviews, sources or scores."""

    try:
        output = await asyncio.wait_for(
            model_gateway.generate(ModelGatewayInput(
                task_name="hr_report_enhancement",
                system_context={"prompt": load_recruitment_prompt("hr_report")},
                structured_input={
                    "goal": report.goal.model_dump(mode="json", exclude={"optional_salary_budget"}),
                    "candidate_rankings": report.candidate_rankings,
                    "candidate_reviews": [
                        {
                            "candidate_id": review.candidate_id,
                            "finding_codes": [finding.code for finding in review.findings],
                            "risk_tags": review.risk_tags,
                            "recommended_action": review.recommended_action,
                        }
                        for review in report.candidate_reviews
                    ],
                    "source_ids": [source.source_id for source in report.knowledge_sources],
                    "deterministic_talent_gaps": report.talent_gaps,
                    "deterministic_next_actions": report.next_actions,
                    "requires_human_decision": report.requires_human_decision,
                },
                output_schema_name="HRReportEnhancement",
                thinking_type="disabled",
                max_completion_tokens=max_completion_tokens,
            )),
            timeout=timeout_seconds,
        )
        try:
            enhancement = HRReportEnhancement.model_validate(output.structured_output)
        except ValidationError as exc:
            _mark_output_error(model_gateway)
            raise ModelGatewayOutputError("HR 报告模型输出未通过结构校验。") from exc
    except (ModelGatewayError, OSError, TimeoutError, ValueError):
        return report.model_copy(update={
            "generation_mode": "RULE_BASED_FALLBACK",
            "fallback_used": True,
            "model_name": None,
        })
    return report.model_copy(update={
        "executive_summary": enhancement.executive_summary,
        "talent_gaps": _unique(report.talent_gaps + enhancement.talent_gaps),
        "next_actions": _unique(report.next_actions + enhancement.next_actions),
        "risk_summary": enhancement.risk_summary,
        "missing_information": enhancement.missing_information,
        "model_name": output.model_name,
        "fallback_used": False,
        "generation_mode": "LLM_ENHANCED",
        "model_duration_ms": output.duration_ms,
        "prompt_tokens": output.prompt_tokens,
        "completion_tokens": output.completion_tokens,
        "total_tokens": output.total_tokens,
    })


def _unique(values: list[str]) -> list[str]:
    return list(dict.fromkeys(value.strip() for value in values if value.strip()))


def _mark_output_error(model_gateway: ModelGateway) -> None:
    marker = getattr(model_gateway, "mark_output_error", None)
    if callable(marker):
        marker()


async def hr_report_node(
    graph_state: Mapping[str, object],
    *,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> dict[str, object]:
    """Execute only the persisted HR-report stage, including idempotency checks."""

    run_id = str(graph_state["run_id"])

    async def execute(
        record: RecruitmentRunRecord,
        execution: RecruitmentNodeExecution,
    ) -> dict[str, object]:
        snapshot = record.snapshot
        state = record.state
        context = state.context
        plan = state.execution_plan
        execution.fallback_used = (
            state.knowledge_summary is not None
            and state.knowledge_summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
        )
        if (
            snapshot.status is not AgentRunStatus.RUNNING
            or snapshot.report is not None
            or snapshot.nodes.get(REPORT_NODE_NAME) is not AgentNodeStatus.WAITING
            or snapshot.nodes.get(JOB_MATCH_NODE_NAME) is AgentNodeStatus.NEEDS_REVIEW
            or snapshot.nodes.get(DECISION_REVIEW_NODE_NAME) is AgentNodeStatus.NEEDS_REVIEW
        ):
            return {}
        if plan is None or state.knowledge_summary is None:
            raise RuntimeError("recruitment report context is unavailable")

        execution.step = "start_hr_report"
        snapshot.status = AgentRunStatus.RUNNING
        snapshot.current_agent = REPORT_NODE_NAME
        snapshot.current_node = REPORT_NODE_NAME
        snapshot.current_candidate_id = None
        snapshot.nodes[REPORT_NODE_NAME] = AgentNodeStatus.RUNNING
        state.status = AgentRunStatus.RUNNING
        state.current_agent = REPORT_NODE_NAME
        state.current_node = REPORT_NODE_NAME
        state.current_candidate_id = None
        state.node_statuses[REPORT_NODE_NAME] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "HR 最终报告节点已启动",
            {"current_action": "汇总真实评分、审查结果、知识来源和人才缺口"},
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
        ))
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "HR 最终报告节点正在准备结构化汇总",
            {
                "current_goal": "先生成确定性报告，再按配置增强允许的叙述字段",
                "candidate_count": len(context.candidate_ids),
                "next_action": "调用招聘报告 Tool",
            },
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
        ))
        report_tool = dependencies.report_tool
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
            "开始生成 HR 结构化报告",
            {"current_action": "执行稳定排序、来源去重和人才缺口汇总"},
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
            tool_name=REPORT_TOOL_NAME,
        ))
        execution.step = "build_hr_report"
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
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
            "HR 结构化报告生成完成",
            {
                "candidate_count": len(report.candidate_rankings),
                "knowledge_source_count": len(report.knowledge_sources),
                "requires_human_decision": report.requires_human_decision,
                "generation_mode": report.generation_mode,
                "model_name": report.model_name,
            },
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
            tool_name=REPORT_TOOL_NAME,
            source_count=len(report.knowledge_sources),
            duration_ms=elapsed_ms(execution.started_at),
            fallback_used=report.fallback_used,
        ))
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.REPORT_GENERATED, AgentNodeStatus.RUNNING,
            "HR 最终报告已生成",
            {"report": report.model_dump(mode="json")},
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
            source_count=len(report.knowledge_sources),
            duration_ms=report.model_duration_ms,
            fallback_used=report.fallback_used,
        ))
        snapshot.nodes[REPORT_NODE_NAME] = AgentNodeStatus.COMPLETED
        state.node_statuses[REPORT_NODE_NAME] = AgentNodeStatus.COMPLETED
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, AgentNodeStatus.COMPLETED,
            "HR 最终报告节点已完成",
            {
                "completed_node": REPORT_NODE_NAME,
                "report_generated": True,
                "requires_human_decision": report.requires_human_decision,
                "generation_mode": report.generation_mode,
                "model_name": report.model_name,
                "next_action": "由 HR 查看报告并完成人工决定",
            },
            agent_name=REPORT_NODE_NAME, node_name=REPORT_NODE_NAME,
            source_count=len(report.knowledge_sources),
            duration_ms=elapsed_ms(execution.started_at),
            fallback_used=report.fallback_used,
        ))

        execution.step = "complete_workflow"
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
            decision_requires_review(review, context.request.goal.confidence_threshold)
            for review in state.decision_reviews.values()
        )
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.WORKFLOW_COMPLETED, AgentNodeStatus.COMPLETED,
            "招聘决策工作流已完成",
            {
                "current_scope": RUN_SCOPE,
                "executed_nodes": plan.executed_nodes,
                "skipped_nodes": plan.skipped_nodes,
                "skip_reasons": {INTERVIEW_NODE_NAME: INTERVIEW_SKIP_REASON},
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
            source_count=len(snapshot.sources),
            duration_ms=elapsed_ms(execution.started_at),
            fallback_used=execution.fallback_used or plan.fallback_used or report.fallback_used,
        ))
        return {}

    return await execute_recruitment_node(
        run_id,
        store,
        dependencies,
        REPORT_NODE_NAME,
        "validate_hr_report_stage",
        execute,
    )

