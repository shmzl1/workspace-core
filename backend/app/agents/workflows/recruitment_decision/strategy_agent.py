"""Static strategy node metadata and deterministic plan construction."""

import asyncio
from collections.abc import Sequence

from pydantic import BaseModel, Field, ValidationError

from app.agents.prompts.loader import load_recruitment_prompt
from app.agents.shared import (
    AgentNodeContract,
    ModelGateway,
    ModelGatewayError,
    ModelGatewayInput,
    ModelGatewayOutputError,
)
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
    forbidden_behaviors=("调用数据库", "生成候选人评分", "修改确定性计划", "自动录用或淘汰"),
)

CURRENT_PHASE = "SPRINT_2_3_INTEGRATED"
NEXT_PHASE = "END_TO_END_VALIDATION"
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
            "通过当前可用知识模式读取岗位标准、招聘目标与招聘规则",
            "使用人工维护的确定性评分算法生成岗位匹配结果",
            "按明确规则完成决策审查并生成结构化 HR 报告",
        ],
        current_phase=CURRENT_PHASE,
        next_phase=NEXT_PHASE,
        plan_notes=[
            "确定性计划先生成，模型仅增强白名单叙述字段。",
            "岗位匹配使用人工维护的确定性评分算法。",
            "决策审查使用明确规则，不静默修改确定性评分。",
            "HR 最终报告以结构化汇总为基线，最终决定由 HR 完成。",
            "面试评估因没有真实结构化评价而跳过，原因：STRUCTURED_INTERVIEW_FEEDBACK_NOT_AVAILABLE。",
            "LLM 或 RAG 不可用时必须明确降级，不得影响确定性评分与工作流完成。",
        ],
    )


class StrategyEnhancement(BaseModel):
    plan_notes: list[str] = Field(default_factory=list)
    next_actions: list[str] = Field(default_factory=list)
    strategy_summary: str | None = None
    risk_reminders: list[str] = Field(default_factory=list)
    missing_information: list[str] = Field(default_factory=list)


async def enhance_recruitment_execution_plan(
    plan: RecruitmentExecutionPlan,
    job_context: RecruitmentJobContext,
    model_gateway: ModelGateway,
    *,
    timeout_seconds: float = 25.0,
    max_completion_tokens: int = 512,
) -> RecruitmentExecutionPlan:
    """Enhance only narrative strategy fields after deterministic planning."""

    try:
        output = await asyncio.wait_for(
            model_gateway.generate(ModelGatewayInput(
                task_name="recruitment_strategy_enhancement",
                system_context={"prompt": load_recruitment_prompt("strategy")},
                structured_input={
                    "goal": plan.goal.model_dump(mode="json", exclude={"optional_salary_budget"}),
                    "job": {
                        "job_id": job_context.job_id,
                        "job_code": job_context.job_code,
                        "job_title": job_context.job_title,
                        "department": job_context.department,
                    },
                    "candidate_count": plan.candidate_count,
                    "executed_nodes": plan.executed_nodes,
                    "skipped_nodes": plan.skipped_nodes,
                    "deterministic_plan_notes": plan.plan_notes,
                    "deterministic_next_actions": plan.next_actions,
                },
                output_schema_name="StrategyEnhancement",
                thinking_type="disabled",
                max_completion_tokens=max_completion_tokens,
            )),
            timeout=timeout_seconds,
        )
        try:
            enhancement = StrategyEnhancement.model_validate(output.structured_output)
        except ValidationError as exc:
            _mark_output_error(model_gateway)
            raise ModelGatewayOutputError("招聘策略模型输出未通过结构校验。") from exc
    except (ModelGatewayError, OSError, TimeoutError, ValueError):
        return plan.model_copy(update={
            "generation_mode": "RULE_BASED_FALLBACK",
            "fallback_used": True,
            "model_name": None,
        })
    return plan.model_copy(update={
        "plan_notes": _unique(plan.plan_notes + enhancement.plan_notes),
        "next_actions": _unique(plan.next_actions + enhancement.next_actions),
        "strategy_summary": enhancement.strategy_summary,
        "risk_reminders": enhancement.risk_reminders,
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

