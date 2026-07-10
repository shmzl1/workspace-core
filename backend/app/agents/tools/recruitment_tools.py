"""Recruitment Tool metadata only; no scoring or report execution."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Protocol

from app.agents.shared import ToolContract
from app.agents.workflows.recruitment_decision.contracts import CandidateProfile, RecruitmentCandidateContext

if TYPE_CHECKING:
    from app.modules.recruitment.services.resume_profile_service import ResumeProfileService


class RecruitmentServiceTool(Protocol):
    def invoke(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


class CandidateProfileTool:
    """Agent Tool that delegates deterministic extraction to its Service."""

    def __init__(self, service: ResumeProfileService | None = None) -> None:
        if service is None:
            from app.modules.recruitment.services.resume_profile_service import ResumeProfileService

            service = ResumeProfileService()
        self.service = service

    def invoke(self, candidate: RecruitmentCandidateContext) -> CandidateProfile:
        return self.service.extract(candidate)


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
    ToolContract(
        name="extract_candidate_profile",
        description="经简历画像 Service 从白名单结构化字段与安全简历片段提取候选人画像。",
        service_boundary="ResumeProfileService",
        permission="candidate.read",
        read_only=True,
        sensitive=True,
        input_fields=("candidate_context",),
        output_fields=("candidate_profile", "evidence_items", "missing_fields"),
    ),
)
