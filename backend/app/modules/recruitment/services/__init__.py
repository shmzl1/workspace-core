"""Recruitment Service boundaries."""

from app.modules.recruitment.services.recruitment_run_context_service import RecruitmentRunContextService
from app.modules.recruitment.services.contracts import (
    CandidateEvaluationServiceProtocol,
    HiringRequirementServiceProtocol,
    RecruitmentReportServiceProtocol,
)

__all__ = [
    "CandidateEvaluationServiceProtocol",
    "HiringRequirementServiceProtocol",
    "RecruitmentReportServiceProtocol",
    "RecruitmentRunContextService",
]

