"""Decision-review node metadata and pure Tool orchestration."""

from collections.abc import Mapping
from time import perf_counter

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.recruitment_support import (
    DECISION_REVIEW_NODE_NAME,
    DECISION_REVIEW_TOOL_NAME,
    INTERVIEW_SKIP_REASON,
    JOB_MATCH_NODE_NAME,
    RecruitmentNodeExecution,
    decision_requires_review,
    elapsed_ms,
    event,
    execute_recruitment_node,
    publish,
)
from app.agents.runtime.run_store import AgentRunStore, RecruitmentRunRecord
from app.agents.shared import AgentEventType, AgentNodeContract, AgentNodeStatus, AgentRunStatus
from app.agents.tools.recruitment_tools import DecisionReviewTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)

DECISION_REVIEW_NODE = AgentNodeContract(
    name="decision_review",
    display_name="决策审查 Agent",
    responsibility="检查证据、来源、必备条件、面试冲突和专业 Agent 分歧。",
    required_inputs=("goal", "candidate_profiles", "job_matches", "interview_evaluations"),
    dependencies=("job_match", "interview_evaluation"),
    allowed_tools=("review_candidate_decision",),
    output_fields=("decision_reviews",),
    forbidden_behaviors=("静默篡改确定性评分", "自动录用或淘汰候选人"),
)


def run_decision_review(
    goal: RecruitmentGoal,
    profile: CandidateProfile,
    job_match: JobMatchSummary,
    interview_evaluation: InterviewEvaluationSummary | None,
    tool: DecisionReviewTool,
) -> DecisionReviewSummary:
    """Invoke the injected review Tool without implementing review rules here."""

    return tool.invoke(goal, profile, job_match, interview_evaluation)


async def decision_review_node(
    graph_state: Mapping[str, object],
    *,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> dict[str, object]:
    """Execute only the persisted decision-review business stage."""

    run_id = str(graph_state["run_id"])

    async def execute(
        record: RecruitmentRunRecord,
        execution: RecruitmentNodeExecution,
    ) -> dict[str, object]:
        snapshot = record.snapshot
        state = record.state
        context = state.context
        snapshot.current_agent = DECISION_REVIEW_NODE_NAME
        snapshot.current_node = DECISION_REVIEW_NODE_NAME
        snapshot.nodes[DECISION_REVIEW_NODE_NAME] = AgentNodeStatus.RUNNING
        state.current_agent = DECISION_REVIEW_NODE_NAME
        state.current_node = DECISION_REVIEW_NODE_NAME
        state.node_statuses[DECISION_REVIEW_NODE_NAME] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "决策审查 Agent 已启动",
            {"current_action": "逐名检查评分、必备条件、证据、画像完整度和面试缺失"},
            agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
        ))
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "决策审查 Agent 正在准备规则审查",
            {
                "current_goal": "用公开确定性公式计算可信度并保留原始评分",
                "candidate_count": len(context.candidate_ids),
                "interview_data_status": INTERVIEW_SKIP_REASON,
                "next_action": "逐名调用决策审查 Tool",
            },
            agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
        ))

        review_tool = dependencies.decision_review_tool
        decision_requires_human_review = False
        for candidate_id in context.candidate_ids:
            candidate_started_at = perf_counter()
            execution.step = "review_candidate_decision"
            snapshot.current_candidate_id = candidate_id
            state.current_candidate_id = candidate_id
            await store.update_snapshot(run_id, snapshot, state)
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
                f"开始审查候选人 #{candidate_id} 的决策依据",
                {"current_action": "执行规则式证据、阈值和风险审查"},
                agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
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
            candidate_needs_review = decision_requires_review(
                review,
                context.request.goal.confidence_threshold,
            )
            decision_requires_human_review = (
                decision_requires_human_review or candidate_needs_review
            )
            await store.update_snapshot(run_id, snapshot, state)
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 决策审查完成",
                {
                    "candidate_id": candidate_id,
                    "confidence": review.confidence,
                    "finding_count": len(review.findings),
                    "requires_review": candidate_needs_review,
                },
                agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
                candidate_id=candidate_id, tool_name=DECISION_REVIEW_TOOL_NAME,
                duration_ms=elapsed_ms(candidate_started_at),
            ))
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.REVIEW_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 审查结果已生成",
                {"decision_review": review.model_dump(mode="json")},
                agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
                candidate_id=candidate_id,
            ))

        execution.step = "complete_decision_review"
        snapshot.current_candidate_id = None
        state.current_candidate_id = None
        review_status = (
            AgentNodeStatus.NEEDS_REVIEW
            if decision_requires_human_review
            else AgentNodeStatus.COMPLETED
        )
        snapshot.nodes[DECISION_REVIEW_NODE_NAME] = review_status
        state.node_statuses[DECISION_REVIEW_NODE_NAME] = review_status
        await store.update_snapshot(run_id, snapshot, state)
        job_match_status = snapshot.nodes.get(JOB_MATCH_NODE_NAME)
        needs_human_review = (
            job_match_status is AgentNodeStatus.NEEDS_REVIEW
            or review_status is AgentNodeStatus.NEEDS_REVIEW
        )
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, review_status,
            "决策审查 Agent 已完成，结果需 HR 复核"
            if decision_requires_human_review else "决策审查 Agent 已完成",
            {
                "completed_node": DECISION_REVIEW_NODE_NAME,
                "reviewed_candidates": len(state.decision_reviews),
                "review_required": decision_requires_human_review,
                "deterministic_scores_preserved": all(
                    review.deterministic_score_preserved
                    for review in state.decision_reviews.values()
                ),
                "next_action": "等待 HR 审查通过后生成 HR 最终报告"
                if needs_human_review
                else "生成 HR 结构化最终报告",
            },
            agent_name=DECISION_REVIEW_NODE_NAME, node_name=DECISION_REVIEW_NODE_NAME,
            duration_ms=elapsed_ms(execution.started_at),
        ))

        if needs_human_review:
            snapshot.status = AgentRunStatus.RUNNING
            snapshot.current_agent = None
            snapshot.current_node = None
            snapshot.current_candidate_id = None
            state.status = AgentRunStatus.RUNNING
            state.current_agent = None
            state.current_node = None
            state.current_candidate_id = None
            await store.update_snapshot(run_id, snapshot, state)
        return {"needs_human_review": needs_human_review}

    return await execute_recruitment_node(
        run_id,
        store,
        dependencies,
        DECISION_REVIEW_NODE_NAME,
        "start_decision_review",
        execute,
    )

