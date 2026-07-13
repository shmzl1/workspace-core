"""Recruitment Service boundaries."""

from app.modules.recruitment.services.contracts import (
    CandidateEvaluationServiceProtocol,
    DecisionReviewServiceProtocol,
    HiringRequirementServiceProtocol,
    RecruitmentReportServiceProtocol,
    RecruitmentKnowledgeServiceProtocol,
)
from app.modules.recruitment.services.candidate_evaluation_service import CandidateEvaluationService
from app.modules.recruitment.services.decision_review_service import DecisionReviewService
from app.modules.recruitment.services.recruitment_knowledge_service import RecruitmentKnowledgeService
from app.modules.recruitment.services.recruitment_report_service import RecruitmentReportService
from app.modules.recruitment.services.recruitment_run_context_service import RecruitmentRunContextService
from app.modules.recruitment.services.resume_profile_service import ResumeProfileService
from app.modules.recruitment.services.local_fallback_knowledge_service import LocalFallbackRecruitmentKnowledgeService
from app.modules.recruitment.services.recruitment_knowledge_adapter import RecruitmentKnowledgeAdapter

__all__ = [
    "CandidateEvaluationService",
    "CandidateEvaluationServiceProtocol",
    "DecisionReviewService",
    "DecisionReviewServiceProtocol",
    "HiringRequirementServiceProtocol",
    "RecruitmentKnowledgeService",
    "RecruitmentKnowledgeAdapter",
    "RecruitmentKnowledgeServiceProtocol",
    "LocalFallbackRecruitmentKnowledgeService",
    "RecruitmentReportService",
    "RecruitmentReportServiceProtocol",
    "RecruitmentRunContextService",
    "ResumeProfileService",
]

