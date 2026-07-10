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
    allowed_tools=("hiring_requirement_service", "recruitment_context"),
    output_fields=("execution_plan",),
    forbidden_behaviors=("调用数据库", "调用 LLM 或 RAG", "生成候选人评分", "自动录用或淘汰"),
)


def build_recruitment_execution_plan(
    request: RecruitmentRunRequest,
    job_context: RecruitmentJobContext,
    candidate_ids: Sequence[int],
    workflow_nodes: Sequence[AgentNodeContract],
) -> RecruitmentExecutionPlan:
    """Build the current plan solely from validated input and static metadata."""

    required_nodes = [node.name for node in workflow_nodes]
    executed_nodes = [RECRUITMENT_STRATEGY_NODE.name]
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
        plan_notes=[
            "当前阶段只执行招聘策略规划。",
            "面试评估必须等待真实结构化面试数据。",
            "后续阶段依次接入简历解析、岗位匹配、决策审查和 HR 最终报告。",
        ],
    )

