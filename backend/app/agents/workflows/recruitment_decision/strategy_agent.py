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

CURRENT_PHASE = "SPRINT_2_3_DETERMINISTIC_INTERMEDIATE"
NEXT_PHASE = "LLM_RAG_INTEGRATION"
EXECUTED_NODES = (
    RECRUITMENT_STRATEGY_NODE.name,
    "resume_parser",
    "job_match",
    "decision_review",
    "hr_report",
)
SKIPPED_NODES = ("interview_evaluation",)


def build_recruitment_execution_plan(
    request: RecruitmentRunRequest,
    job_context: RecruitmentJobContext,
    candidate_ids: Sequence[int],
    workflow_nodes: Sequence[AgentNodeContract],
    interview_candidate_ids: Sequence[int] = (),
) -> RecruitmentExecutionPlan:
    """Build the current plan solely from validated input and static metadata."""

    required_nodes = [node.name for node in workflow_nodes]
    normalized_goal = request.goal.model_copy(
        update={"job_title": job_context.job_title, "department": job_context.department}
    )
    return RecruitmentExecutionPlan(
        goal=normalized_goal,
        candidate_ids=list(candidate_ids),
        candidate_count=len(candidate_ids),
        required_nodes=required_nodes,
        executed_nodes=list(EXECUTED_NODES),
        skipped_nodes=list(SKIPPED_NODES),
        resume_parse_required=True,
        interview_candidate_ids=list(interview_candidate_ids),
        next_actions=[
            f"解析 {len(candidate_ids)} 名候选人的结构化简历上下文",
            "通过 LOCAL_HYBRID_FALLBACK 读取当前岗位标准、招聘目标与招聘规则",
            "使用人工维护的确定性评分算法生成岗位匹配结果",
            "按明确规则完成决策审查并生成结构化 HR 报告",
        ],
        current_phase=CURRENT_PHASE,
        next_phase=NEXT_PHASE,
        plan_notes=[
            "当前为确定性中间版本。",
            "岗位匹配使用人工维护的确定性评分算法。",
            "决策审查使用明确规则，不静默修改确定性评分。",
            "HR 最终报告使用结构化汇总，最终决定由 HR 完成。",
            "面试评估因没有真实结构化评价而跳过，原因：STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE。",
            "尚未接入大模型、LangGraph、ChromaDB 或真实本地 RAG；企业知识继续使用 LOCAL_HYBRID_FALLBACK。",
        ],
    )

