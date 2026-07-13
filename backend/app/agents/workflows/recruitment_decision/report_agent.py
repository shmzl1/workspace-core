"""HR-report Tool orchestration and bounded model narrative enhancement."""

from pydantic import BaseModel, Field, ValidationError

from app.agents.prompts.loader import load_recruitment_prompt
from app.agents.shared import (
    AgentNodeContract,
    ModelGateway,
    ModelGatewayError,
    ModelGatewayInput,
    ModelGatewayOutputError,
)
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
) -> HRReportSummary:
    """Enhance narrative fields without changing rankings, reviews, sources or scores."""

    try:
        output = await model_gateway.generate(ModelGatewayInput(
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
        ))
        try:
            enhancement = HRReportEnhancement.model_validate(output.structured_output)
        except ValidationError as exc:
            _mark_output_error(model_gateway)
            raise ModelGatewayOutputError("HR 报告模型输出未通过结构校验。") from exc
    except (ModelGatewayError, OSError, ValueError):
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

