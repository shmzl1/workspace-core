"""Protocols for professional recruitment Services."""

from typing import Protocol

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    HRReportSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentGoal,
    RecruitmentRunContext,
)


class CandidateEvaluationServiceProtocol(Protocol):
    def evaluate(
        self,
        context: RecruitmentRunContext,
        profile: CandidateProfile,
        rubric: JobRubric,
        knowledge: EnterpriseKnowledgeSummary,
    ) -> JobMatchSummary: ...


class HiringRequirementServiceProtocol(Protocol):
    def get_goal(self, job_id: int) -> RecruitmentGoal: ...

    def get_rubric(self, job_id: int) -> JobRubric: ...


class DecisionReviewServiceProtocol(Protocol):
    def review(
        self,
        goal: RecruitmentGoal,
        profile: CandidateProfile,
        job_match: JobMatchSummary,
        interview_evaluation: InterviewEvaluationSummary | None = None,
    ) -> DecisionReviewSummary: ...


class RecruitmentReportServiceProtocol(Protocol):
    def build_report(
        self,
        goal: RecruitmentGoal,
        job_matches: dict[int, JobMatchSummary],
        decision_reviews: dict[int, DecisionReviewSummary],
        knowledge: EnterpriseKnowledgeSummary,
        candidate_profiles: dict[int, CandidateProfile],
        interview_evaluations: dict[int, InterviewEvaluationSummary],
    ) -> HRReportSummary: ...


class RecruitmentKnowledgeServiceProtocol(Protocol):
    async def retrieve(
        self,
        context: RecruitmentRunContext,
    ) -> tuple[EnterpriseKnowledgeSummary, JobRubric]: ...
