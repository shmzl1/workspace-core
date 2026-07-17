"""Job-match node metadata and pure Tool orchestration."""

from collections.abc import Mapping
from time import perf_counter

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.recruitment_support import (
    JOB_MATCH_NODE_NAME,
    JOB_MATCH_TOOL_NAME,
    RecruitmentNodeExecution,
    elapsed_ms,
    event,
    execute_recruitment_node,
    publish,
)
from app.agents.runtime.run_store import AgentRunStore, RecruitmentRunRecord
from app.agents.shared import AgentEventType, AgentNodeContract, AgentNodeStatus
from app.agents.tools.recruitment_tools import CandidateEvaluationTool
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    EnterpriseKnowledgeSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentRunContext,
)

JOB_MATCH_NODE = AgentNodeContract(
    name="job_match",
    display_name="岗位匹配 Agent",
    responsibility="依据候选人画像和岗位标准调用专业 Service，汇总确定性评分与技能缺口。",
    required_inputs=("context", "candidate_profiles", "job_rubric", "knowledge_summary"),
    dependencies=("resume_parser",),
    allowed_tools=("evaluate_candidate",),
    output_fields=("job_matches",),
    forbidden_behaviors=("自行编造确定性评分", "绕过必备条件", "直接调用 human_only"),
)


def run_job_match(
    context: RecruitmentRunContext,
    profile: CandidateProfile,
    rubric: JobRubric,
    knowledge: EnterpriseKnowledgeSummary,
    tool: CandidateEvaluationTool,
) -> JobMatchSummary:
    """Invoke the injected Tool without scoring or event publication here."""

    return tool.invoke(context, profile, rubric, knowledge)


async def job_match_node(
    graph_state: Mapping[str, object],
    *,
    store: AgentRunStore,
    dependencies: RecruitmentRunnerDependencies,
) -> dict[str, object]:
    """Execute only the persisted deterministic job-match business stage."""

    run_id = str(graph_state["run_id"])

    async def execute(
        record: RecruitmentRunRecord,
        execution: RecruitmentNodeExecution,
    ) -> dict[str, object]:
        snapshot = record.snapshot
        state = record.state
        context = state.context
        if state.job_rubric is None or state.knowledge_summary is None:
            raise RuntimeError("recruitment knowledge context is unavailable")

        snapshot.current_agent = JOB_MATCH_NODE_NAME
        snapshot.current_node = JOB_MATCH_NODE_NAME
        snapshot.nodes[JOB_MATCH_NODE_NAME] = AgentNodeStatus.RUNNING
        state.current_agent = JOB_MATCH_NODE_NAME
        state.current_node = JOB_MATCH_NODE_NAME
        state.node_statuses[JOB_MATCH_NODE_NAME] = AgentNodeStatus.RUNNING
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_STARTED, AgentNodeStatus.RUNNING,
            "岗位匹配 Agent 已启动",
            {"current_action": "逐名调用确定性候选人评估 Tool", "candidate_count": len(context.candidate_ids)},
            agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
        ))
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_THINKING, AgentNodeStatus.RUNNING,
            "岗位匹配 Agent 正在准备确定性评分",
            {
                "current_goal": "保留人工维护评分结果并汇总技能缺口与证据",
                "candidate_count": len(context.candidate_ids),
                "scoring_mode": "DETERMINISTIC_HUMAN_ONLY",
                "next_action": "逐名调用候选人评估 Tool",
            },
            agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
        ))

        evaluation_tool = dependencies.candidate_evaluation_tool
        job_match_requires_review = False
        for candidate_id in context.candidate_ids:
            candidate_started_at = perf_counter()
            execution.step = "evaluate_candidate"
            snapshot.current_candidate_id = candidate_id
            state.current_candidate_id = candidate_id
            await store.update_snapshot(run_id, snapshot, state)
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_STARTED, AgentNodeStatus.RUNNING,
                f"开始评估候选人 #{candidate_id} 的岗位匹配",
                {"current_action": "调用确定性评分边界并校验证据引用"},
                agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
                candidate_id=candidate_id, tool_name=JOB_MATCH_TOOL_NAME,
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
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.TOOL_COMPLETED, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 岗位匹配评估完成",
                {
                    "candidate_id": candidate_id,
                    "overall_score": job_match.overall_score,
                    "job_match_score": job_match.job_match_score,
                    "requires_review": candidate_needs_review,
                },
                agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
                candidate_id=candidate_id, tool_name=JOB_MATCH_TOOL_NAME,
                duration_ms=elapsed_ms(candidate_started_at),
            ))
            await publish(store, event(
                run_id, snapshot.trace_id, AgentEventType.INTERMEDIATE_RESULT, AgentNodeStatus.RUNNING,
                f"候选人 #{candidate_id} 岗位匹配结果已生成",
                {"job_match_summary": job_match.model_dump(mode="json")},
                agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
                candidate_id=candidate_id,
                source_count=len(job_match.knowledge_sources),
            ))

        execution.step = "complete_job_match"
        snapshot.current_candidate_id = None
        state.current_candidate_id = None
        job_match_status = (
            AgentNodeStatus.NEEDS_REVIEW if job_match_requires_review else AgentNodeStatus.COMPLETED
        )
        snapshot.nodes[JOB_MATCH_NODE_NAME] = job_match_status
        state.node_statuses[JOB_MATCH_NODE_NAME] = job_match_status
        await store.update_snapshot(run_id, snapshot, state)
        await publish(store, event(
            run_id, snapshot.trace_id, AgentEventType.AGENT_COMPLETED, job_match_status,
            "岗位匹配 Agent 已完成，存在结果需人工复核"
            if job_match_requires_review else "岗位匹配 Agent 已完成",
            {
                "completed_node": JOB_MATCH_NODE_NAME,
                "evaluated_candidates": len(state.job_matches),
                "review_required": job_match_requires_review,
                "next_action": "跳过无真实数据的面试评估并执行决策审查",
            },
            agent_name=JOB_MATCH_NODE_NAME, node_name=JOB_MATCH_NODE_NAME,
            source_count=len(snapshot.sources),
            duration_ms=elapsed_ms(execution.started_at),
        ))
        return {"needs_human_review": job_match_requires_review}

    return await execute_recruitment_node(
        run_id,
        store,
        dependencies,
        JOB_MATCH_NODE_NAME,
        "validate_knowledge_context",
        execute,
    )

