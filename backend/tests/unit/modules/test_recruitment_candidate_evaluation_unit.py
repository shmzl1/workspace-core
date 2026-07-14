from datetime import date

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    EnterpriseKnowledgeSummary,
    JobRubric,
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
)
from app.modules.recruitment.services.candidate_evaluation_service import CandidateEvaluationService


def context(required_skills: list[str]) -> RecruitmentRunContext:
    goal = RecruitmentGoal(job_id=1, job_title="Engineer", department="R&D", target_headcount=1, required_skills=required_skills)
    job = RecruitmentJobContext(
        job_id=1, job_code="ENG-1", job_title="Engineer", department="R&D", status="OPEN",
        source_version="v1", effective_date=date(2026, 7, 14),
    )
    return RecruitmentRunContext(request=RecruitmentRunRequest(goal=goal), job=job)


def knowledge() -> EnterpriseKnowledgeSummary:
    return EnterpriseKnowledgeSummary(job_id=1, job_code="ENG-1", standard_version="v1", effective_date=date(2026, 7, 14))


def score(_payload: dict) -> dict:
    return {
        "status": "scored",
        "overall_score": 80,
        "job_match_score": 82,
        "score_breakdown": {"skill": 80, "experience": 75, "project": 70, "education": 85, "risk": 90},
        "recommended_action": "REVIEW",
        "risk_tags": [],
    }


def test_missing_required_skill_forces_human_review_even_with_valid_score() -> None:
    result = CandidateEvaluationService(score_loader=lambda: score).evaluate(
        context(["Python", "FastAPI"]),
        CandidateProfile(candidate_id=1, skills=[" python "], normalized_skills=["PYTHON"]),
        JobRubric(job_id=1),
        knowledge(),
    )

    assert result.overall_score == 80
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["FastAPI"]
    assert result.must_have_passed is False
    assert result.requires_review is True


def test_invalid_score_response_returns_review_required_without_fabricating_score() -> None:
    result = CandidateEvaluationService(score_loader=lambda: lambda _payload: {"overall_score": 101}).evaluate(
        context(["Python"]), CandidateProfile(candidate_id=1, skills=["Python"]), JobRubric(job_id=1), knowledge()
    )

    assert result.overall_score is None
    assert result.job_match_score is None
    assert result.requires_review is True
