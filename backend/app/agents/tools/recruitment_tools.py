"""Recruitment Tools that delegate only to professional Services."""

from __future__ import annotations

from typing import TYPE_CHECKING, Mapping, Protocol

from app.agents.shared import ToolContract
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    HRReportSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentCandidateContext,
    RecruitmentGoal,
    RecruitmentRunContext,
)

if TYPE_CHECKING:
    from app.modules.recruitment.services.candidate_evaluation_service import (
        CandidateEvaluationService,
    )
    from app.modules.recruitment.services.decision_review_service import DecisionReviewService
    from app.modules.recruitment.services.recruitment_report_service import (
        RecruitmentReportService,
    )
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


class CandidateEvaluationTool:
    """Delegate deterministic job matching to CandidateEvaluationService."""

    def __init__(self, service: CandidateEvaluationService | None = None) -> None:
        if service is None:
            from app.modules.recruitment.services.candidate_evaluation_service import (
                CandidateEvaluationService,
            )

            service = CandidateEvaluationService()
        self.service = service

    def invoke(
        self,
        context: RecruitmentRunContext,
        profile: CandidateProfile,
        rubric: JobRubric,
        knowledge: EnterpriseKnowledgeSummary,
    ) -> JobMatchSummary:
        return self.service.evaluate(context, profile, rubric, knowledge)


class DecisionReviewTool:
    """Delegate evidence and threshold review to DecisionReviewService."""

    def __init__(self, service: DecisionReviewService | None = None) -> None:
        if service is None:
            from app.modules.recruitment.services.decision_review_service import (
                DecisionReviewService,
            )

            service = DecisionReviewService()
        self.service = service

    def invoke(
        self,
        goal: RecruitmentGoal,
        profile: CandidateProfile,
        job_match: JobMatchSummary,
        interview_evaluation: InterviewEvaluationSummary | None,
    ) -> DecisionReviewSummary:
        return self.service.review(goal, profile, job_match, interview_evaluation)


class RecruitmentReportTool:
    """Delegate structured HR report generation to RecruitmentReportService."""

    def __init__(self, service: RecruitmentReportService | None = None) -> None:
        if service is None:
            from app.modules.recruitment.services.recruitment_report_service import (
                RecruitmentReportService,
            )

            service = RecruitmentReportService()
        self.service = service

    def invoke(
        self,
        goal: RecruitmentGoal,
        job_matches: dict[int, JobMatchSummary],
        decision_reviews: dict[int, DecisionReviewSummary],
        knowledge: EnterpriseKnowledgeSummary,
        candidate_profiles: dict[int, CandidateProfile],
        interview_evaluations: dict[int, InterviewEvaluationSummary],
    ) -> HRReportSummary:
        return self.service.build_report(
            goal,
            job_matches,
            decision_reviews,
            knowledge,
            candidate_profiles,
            interview_evaluations,
        )


RECRUITMENT_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="evaluate_candidate",
        description="经专业 Service 调用人工维护的确定性评分边界并生成岗位匹配结果。",
        service_boundary="CandidateEvaluationService",
        permission="candidate.score",
        read_only=True,
        sensitive=True,
        input_fields=("run_context", "candidate_profile", "job_rubric", "knowledge_summary"),
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
    ToolContract(
        name="review_candidate_decision",
        description="经规则式 Service 审查评分、证据、画像完整度、阈值和面试数据。",
        service_boundary="DecisionReviewService",
        permission="candidate.score",
        read_only=True,
        sensitive=True,
        input_fields=(
            "recruitment_goal",
            "candidate_profile",
            "job_match_summary",
            "interview_evaluation",
        ),
        output_fields=("decision_review",),
    ),
    ToolContract(
        name="build_recruitment_report",
        description="经结构化汇总 Service 生成保留 HR 最终决定权的招聘报告。",
        service_boundary="RecruitmentReportService",
        permission="recruitment.read",
        read_only=True,
        sensitive=True,
        input_fields=(
            "recruitment_goal",
            "job_matches",
            "decision_reviews",
            "knowledge_summary",
            "candidate_profiles",
            "interview_evaluations",
        ),
        output_fields=("report",),
    ),
)
