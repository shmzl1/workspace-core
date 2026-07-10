"""Protocols for future professional recruitment Services."""

from collections.abc import Sequence
from typing import Protocol

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    HRReportSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentGoal,
)


class CandidateEvaluationServiceProtocol(Protocol):
    def evaluate(self, profile: CandidateProfile, rubric: JobRubric) -> JobMatchSummary: ...


class HiringRequirementServiceProtocol(Protocol):
    def get_goal(self, job_id: int) -> RecruitmentGoal: ...

    def get_rubric(self, job_id: int) -> JobRubric: ...


class RecruitmentReportServiceProtocol(Protocol):
    def build_summary(
        self,
        goal: RecruitmentGoal,
        reviews: Sequence[DecisionReviewSummary],
    ) -> HRReportSummary: ...
