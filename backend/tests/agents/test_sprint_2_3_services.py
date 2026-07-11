"""Sprint 2.3 deterministic recruitment Service acceptance tests."""

from datetime import date
from typing import Any

from app.agents.shared import KnowledgeSourceReference
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewFinding,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
    ResumeEvidenceItem,
)
from app.modules.recruitment.services.candidate_evaluation_service import (
    CandidateEvaluationService,
)
from app.modules.recruitment.services.decision_review_service import DecisionReviewService
from app.modules.recruitment.services.recruitment_report_service import RecruitmentReportService


def build_context(
    *,
    required_skills: list[str] | None = None,
    preferred_skills: list[str] | None = None,
) -> RecruitmentRunContext:
    goal = RecruitmentGoal(
        job_id=7,
        job_title="AI 后端工程师",
        department="技术部",
        target_headcount=1,
        required_skills=required_skills if required_skills is not None else ["Python"],
        preferred_skills=preferred_skills if preferred_skills is not None else ["RAG"],
        min_experience_months=24,
        score_threshold=70,
        confidence_threshold=75,
    )
    return RecruitmentRunContext(
        request=RecruitmentRunRequest(goal=goal, candidate_ids=[1]),
        job=RecruitmentJobContext(
            job_id=7,
            job_code="JOB-AI-007",
            job_title="数据库岗位标题",
            department="技术部",
            status="OPEN",
            required_skills=["Java"],
            preferred_skills=["Kubernetes"],
            min_experience_months=36,
            source_version="job-v7",
            effective_date=date(2026, 7, 10),
        ),
        candidate_ids=[1],
    )


def build_profile(candidate_id: int = 1, skills: list[str] | None = None) -> CandidateProfile:
    actual_skills = skills if skills is not None else ["Python"]
    evidence = [
        ResumeEvidenceItem(
            evidence_id=f"candidate-{candidate_id}-skill-1",
            capability=actual_skills[0],
            excerpt=f"结构化技能字段：{actual_skills[0]}",
            source_section="structured_skills",
            supports=True,
            confidence=0.9,
        )
    ] if actual_skills else []
    return CandidateProfile(
        candidate_id=candidate_id,
        skills=actual_skills,
        normalized_skills=actual_skills,
        experience_months=36,
        education=["本科"],
        projects=["Agent 平台"],
        project_roles=["后端开发"],
        project_technologies=["FastAPI"],
        measurable_achievements=["接口延迟降低 20%"],
        certificates=["软件设计师"],
        availability="2026-08-01",
        evidence_items=evidence,
    )


def build_knowledge() -> EnterpriseKnowledgeSummary:
    return EnterpriseKnowledgeSummary(
        job_id=7,
        job_code="JOB-AI-007",
        standard_version="job-v7",
        effective_date=date(2026, 7, 10),
        sources=[
            KnowledgeSourceReference(
                source_id="source-a",
                title="岗位标准",
                version="v1",
            )
        ],
    )


def valid_score(_payload: dict[str, Any]) -> dict[str, Any]:
    return {
        "status": "scored",
        "overall_score": 82.5,
        "match_score": 86.0,
        "score_breakdown": {
            "skill": 80,
            "experience": 90,
            "project": 75,
            "education": 82,
            "risk": 85,
        },
        "risk_tags": [],
        "recommended_action": "建议进入初筛复核",
    }


def test_candidate_evaluation_maps_human_score_and_uses_goal_payload() -> None:
    captured: dict[str, Any] = {}

    def scorer(payload: dict[str, Any]) -> dict[str, Any]:
        captured.update(payload)
        return valid_score(payload)

    context = build_context()
    profile = build_profile()
    result = CandidateEvaluationService(score_loader=lambda: scorer).evaluate(
        context,
        profile,
        JobRubric(job_id=7, version="job-v7"),
        build_knowledge(),
    )

    assert result.overall_score == 82.5
    assert result.job_match_score == 86.0
    assert result.dimension_scores == {
        "skill": 80.0,
        "experience": 90.0,
        "project": 75.0,
        "education": 82.0,
        "risk": 85.0,
    }
    assert result.evidence_ids == ["candidate-1-skill-1"]
    assert result.scoring_mode == "DETERMINISTIC_HUMAN_ONLY"
    assert captured["job"]["required_skills"] == ["Python"]
    assert captured["job"]["preferred_skills"] == ["RAG"]
    assert captured["job"]["min_experience_months"] == 24
    assert "weights" not in captured
    assert set(captured["candidate"]) == {
        "skills",
        "normalized_skills",
        "experience_months",
        "education",
        "projects",
        "project_roles",
        "project_technologies",
        "measurable_achievements",
        "certificates",
        "availability",
    }


def test_candidate_evaluation_never_fabricates_score_when_algorithm_unavailable() -> None:
    result = CandidateEvaluationService(score_loader=lambda: None).evaluate(
        build_context(),
        build_profile(),
        JobRubric(job_id=7),
        build_knowledge(),
    )

    assert result.overall_score is None
    assert result.job_match_score is None
    assert result.dimension_scores == {}
    assert result.requires_review is True
    assert result.recommended_action == "确定性评分暂不可用，请人工复核"
    assert result.matched_skills == ["Python"]
    assert result.missing_skills == ["RAG"]


def test_preferred_skill_gap_does_not_fail_must_have_check() -> None:
    service = CandidateEvaluationService(score_loader=lambda: valid_score)
    preferred_only_gap = service.evaluate(
        build_context(required_skills=["Python"], preferred_skills=["RAG"]),
        build_profile(skills=["Python"]),
        JobRubric(job_id=7),
        build_knowledge(),
    )
    required_gap = service.evaluate(
        build_context(required_skills=["Python", "FastAPI"], preferred_skills=[]),
        build_profile(skills=["Python"]),
        JobRubric(job_id=7),
        build_knowledge(),
    )

    assert preferred_only_gap.must_have_passed is True
    assert preferred_only_gap.requires_review is False
    assert preferred_only_gap.missing_skills == ["RAG"]
    assert required_gap.must_have_passed is False
    assert required_gap.requires_review is True
    assert required_gap.recommended_action == "必备技能未完全满足，建议人工复核"


def test_decision_review_preserves_score_and_uses_stable_confidence_formula() -> None:
    goal = build_context().request.goal
    profile = build_profile()
    job_match = JobMatchSummary(
        candidate_id=1,
        overall_score=82.5,
        job_match_score=86,
        dimension_scores={"skill": 80},
        must_have_passed=True,
        matched_skills=["Python"],
        missing_skills=["RAG"],
        evidence_ids=["candidate-1-skill-1"],
    )
    original = job_match.model_dump(mode="json")

    review = DecisionReviewService().review(goal, profile, job_match, None)

    assert job_match.model_dump(mode="json") == original
    assert review.deterministic_score_preserved is True
    assert review.confidence == 70.0
    assert review.review_mode == "RULE_BASED_INTERMEDIATE"
    codes = {finding.code for finding in review.findings}
    assert "INTERVIEW_DATA_MISSING" in codes
    assert "CONFIDENCE_BELOW_THRESHOLD" in codes


def test_recruitment_report_sorts_scores_and_deduplicates_real_sources() -> None:
    goal = build_context().request.goal
    source_a = KnowledgeSourceReference(source_id="source-a", title="岗位标准")
    source_b = KnowledgeSourceReference(source_id="source-b", title="招聘规则")
    knowledge = build_knowledge().model_copy(update={"sources": [source_a, source_a]})
    job_matches = {
        1: JobMatchSummary(
            candidate_id=1,
            overall_score=80,
            job_match_score=80,
            must_have_passed=True,
            missing_skills=["RAG"],
            knowledge_sources=[source_b],
        ),
        2: JobMatchSummary(
            candidate_id=2,
            overall_score=None,
            job_match_score=None,
            must_have_passed=True,
            missing_skills=["RAG"],
            knowledge_sources=[source_a],
            requires_review=True,
        ),
        3: JobMatchSummary(
            candidate_id=3,
            overall_score=80,
            job_match_score=80,
            must_have_passed=True,
            missing_skills=["RAG"],
            knowledge_sources=[source_a],
        ),
    }
    decision_reviews = {
        candidate_id: DecisionReviewSummary(
            candidate_id=candidate_id,
            confidence=80 if candidate_id != 2 else 40,
            findings=(
                []
                if candidate_id != 2
                else [
                    DecisionReviewFinding(
                        code="DETERMINISTIC_SCORE_UNAVAILABLE",
                        severity="HIGH",
                        summary="确定性评分不可用。",
                        requires_human_review=True,
                    )
                ]
            ),
        )
        for candidate_id in (1, 2, 3)
    }
    profiles = {candidate_id: build_profile(candidate_id) for candidate_id in (1, 2, 3)}

    report = RecruitmentReportService().build_report(
        goal,
        job_matches,
        decision_reviews,
        knowledge,
        profiles,
        {},
    )

    assert report.candidate_rankings == [1, 3, 2]
    assert [review.candidate_id for review in report.candidate_reviews] == [1, 3, 2]
    assert [source.source_id for source in report.knowledge_sources] == ["source-a", "source-b"]
    assert "所有已匹配候选人均缺少技能：RAG" in report.talent_gaps
    assert "当前候选人整体缺少真实结构化面试评价" in report.talent_gaps
    assert report.requires_human_decision is True
    assert report.generation_mode == "RULE_BASED_INTERMEDIATE"
