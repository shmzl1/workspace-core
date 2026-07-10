"""Static strategy node metadata and deterministic plan construction."""

from collections.abc import Sequence

from app.agents.shared import AgentNodeContract
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentExecutionPlan,
    RecruitmentJobContext,
    RecruitmentRunRequest,
)

RECRUITMENT_STRATEGY_NODE = AgentNodeContract(
    name="recruitment_strategy",
    display_name="招聘策略 Agent",
    responsibility="读取已校验的企业招聘目标并生成专业 Agent 的结构化执行计划。",
    required_inputs=("request", "job_context", "candidate_ids", "workflow_nodes"),
    allowed_tools=("hiring_requirement_service", "recruitment_context", "retrieve_enterprise_knowledge"),
    output_fields=("execution_plan",),
    forbidden_behaviors=("调用数据库", "调用 LLM 或 RAG", "生成候选人评分", "自动录用或淘汰"),
)


def build_recruitment_execution_plan(
    request: RecruitmentRunRequest,
    job_context: RecruitmentJobContext,
    candidate_ids: Sequence[int],
    workflow_nodes: Sequence[AgentNodeContract],
    interview_candidate_ids: Sequence[int] = (),
) -> RecruitmentExecutionPlan:
    """Build the current plan solely from validated input and static metadata."""

    required_nodes = [node.name for node in workflow_nodes]
    executed_nodes = [RECRUITMENT_STRATEGY_NODE.name, "resume_parser"]
    skipped_nodes = [name for name in required_nodes if name not in executed_nodes]
    normalized_goal = request.goal.model_copy(
        update={"job_title": job_context.job_title, "department": job_context.department}
    )
    return RecruitmentExecutionPlan(
        goal=normalized_goal,
        candidate_ids=list(candidate_ids),
        candidate_count=len(candidate_ids),
        required_nodes=required_nodes,
        executed_nodes=executed_nodes,
        skipped_nodes=skipped_nodes,
        resume_parse_required=True,
        interview_candidate_ids=list(interview_candidate_ids),
        next_actions=[
            f"解析 {len(candidate_ids)} 名候选人的结构化简历上下文",
            "检索当前岗位标准、招聘目标与招聘规则",
            "为 Sprint 2.3 岗位匹配保留结构化画像和岗位 Rubric",
        ],
        current_phase="SPRINT_2_2_STRATEGY_RESUME_KNOWLEDGE",
        next_phase="SPRINT_2_3",
        plan_notes=[
            "当前阶段执行招聘策略规划、企业知识检索和简历解析。",
            "LLM 未接入，简历解析使用白名单数据库字段和安全片段确定性回退。",
            "面试评估必须等待真实结构化面试数据。",
            "后续阶段接入岗位匹配、决策审查和 HR 最终报告。",
        ],
    )

