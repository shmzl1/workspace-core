"""Recruitment Tool metadata only; no scoring or report execution."""

from typing import Mapping, Protocol

from app.agents.shared import ToolContract


class RecruitmentServiceTool(Protocol):
    def invoke(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


RECRUITMENT_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="evaluate_candidate",
        description="经专业 Service 调用现有招聘服务与确定性评分边界。",
        service_boundary="CandidateEvaluationServiceProtocol",
        permission="candidate.score",
        read_only=False,
        sensitive=True,
        input_fields=("candidate_profile", "job_rubric"),
        output_fields=("job_match_summary",),
    ),
    ToolContract(
        name="read_hiring_requirement",
        description="读取结构化企业招聘目标与岗位标准。",
        service_boundary="HiringRequirementServiceProtocol",
        permission="recruitment.read",
        read_only=True,
        sensitive=False,
        input_fields=("job_id",),
        output_fields=("recruitment_goal", "job_rubric"),
    ),
)
