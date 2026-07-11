"""Deterministic candidate evaluation for Sprint 2.3 Agent runs."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from math import isfinite
from typing import Any

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    EnterpriseKnowledgeSummary,
    JobMatchSummary,
    JobRubric,
    RecruitmentRunContext,
)
from app.modules.recruitment.services.contracts import CandidateEvaluationServiceProtocol
from app.shared.human_only_bridge import HumanOnlyContract, load_human_only_function

RESUME_SCORING_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.resume_scoring",
    file_path="backend/app/human_only/resume_scoring.py",
    function_name="score_resume",
    not_ready_message="确定性评分暂不可用，请人工复核",
)
SCORING_MODE = "DETERMINISTIC_HUMAN_ONLY"
SCORING_UNAVAILABLE_ACTION = "确定性评分暂不可用，请人工复核"
REQUIRED_SKILL_REVIEW_ACTION = "必备技能未完全满足，建议人工复核"
LOW_DIMENSION_THRESHOLD = 60.0
DIMENSION_NAMES = {
    "skill": "技能匹配",
    "experience": "经验匹配",
    "project": "项目经历",
    "education": "教育背景",
    "risk": "风险维度",
}

ScoreResumeFunction = Callable[[dict[str, Any]], dict[str, Any]]
ScoreResumeLoader = Callable[[], ScoreResumeFunction | None]


@dataclass(frozen=True)
class _ParsedScore:
    overall_score: float
    job_match_score: float
    dimension_scores: dict[str, float]
    recommended_action: str
    risk_tags: list[str]


class CandidateEvaluationService:
    """Adapt detached Agent inputs to the human-maintained scoring boundary."""

    def __init__(self, score_loader: ScoreResumeLoader | None = None) -> None:
        self._score_loader = score_loader or self._load_score_resume

    def evaluate(
        self,
        context: RecruitmentRunContext,
        profile: CandidateProfile,
        rubric: JobRubric,
        knowledge: EnterpriseKnowledgeSummary,
    ) -> JobMatchSummary:
        goal = context.request.goal
        required_skills = self._unique(goal.required_skills or context.job.required_skills)
        preferred_skills = self._unique(goal.preferred_skills or context.job.preferred_skills)
        matched_skills, missing_required, missing_preferred = self._match_skills(
            profile,
            required_skills,
            preferred_skills,
        )
        missing_skills = [*missing_required, *missing_preferred]
        must_have_passed = not missing_required
        evidence_ids = self._evidence_ids(profile)
        payload = self._build_payload(
            context,
            profile,
            rubric,
            required_skills,
            preferred_skills,
        )

        scorer = self._safe_load_scorer()
        if scorer is None:
            return self._unavailable_summary(
                profile,
                knowledge,
                matched_skills,
                missing_required,
                missing_preferred,
                evidence_ids,
                must_have_passed,
            )

        try:
            raw_result = scorer(payload)
        except Exception:
            return self._unavailable_summary(
                profile,
                knowledge,
                matched_skills,
                missing_required,
                missing_preferred,
                evidence_ids,
                must_have_passed,
            )

        parsed = self._parse_score(raw_result)
        if parsed is None:
            return self._unavailable_summary(
                profile,
                knowledge,
                matched_skills,
                missing_required,
                missing_preferred,
                evidence_ids,
                must_have_passed,
            )

        questions = self._interview_questions(
            missing_required,
            missing_preferred,
            parsed.dimension_scores,
            parsed.risk_tags,
        )
        recommended_action = (
            parsed.recommended_action
            if must_have_passed
            else REQUIRED_SKILL_REVIEW_ACTION
        )
        return JobMatchSummary(
            candidate_id=profile.candidate_id,
            overall_score=parsed.overall_score,
            job_match_score=parsed.job_match_score,
            dimension_scores=parsed.dimension_scores,
            must_have_passed=must_have_passed,
            matched_skills=matched_skills,
            missing_skills=missing_skills,
            evidence_ids=evidence_ids,
            knowledge_sources=list(knowledge.sources),
            suggested_interview_questions=questions,
            recommended_action=recommended_action,
            scoring_mode=SCORING_MODE,
            requires_review=not must_have_passed,
        )

    @staticmethod
    def _load_score_resume() -> ScoreResumeFunction | None:
        return load_human_only_function(RESUME_SCORING_CONTRACT)

    def _safe_load_scorer(self) -> ScoreResumeFunction | None:
        try:
            return self._score_loader()
        except Exception:
            return None

    @classmethod
    def _build_payload(
        cls,
        context: RecruitmentRunContext,
        profile: CandidateProfile,
        rubric: JobRubric,
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> dict[str, Any]:
        goal = context.request.goal
        scoring_skills = cls._unique([*profile.skills, *profile.normalized_skills])
        return {
            "job": {
                "id": goal.job_id,
                "job_id": goal.job_id,
                "job_code": context.job.job_code,
                "title": goal.job_title or context.job.job_title,
                "required_skills": required_skills,
                "preferred_skills": preferred_skills,
                "min_experience_months": goal.min_experience_months,
            },
            "candidate": {
                "skills": scoring_skills,
                "normalized_skills": list(profile.normalized_skills),
                "experience_months": profile.experience_months,
                "education": list(profile.education),
                "projects": list(profile.projects),
                "project_roles": list(profile.project_roles),
                "project_technologies": list(profile.project_technologies),
                "measurable_achievements": list(profile.measurable_achievements),
                "certificates": list(profile.certificates),
                "availability": profile.availability,
            },
            "rubric": {
                "job_id": rubric.job_id,
                "version": rubric.version,
                "requirements": [item.model_dump(mode="json") for item in rubric.requirements],
            },
        }

    @classmethod
    def _match_skills(
        cls,
        profile: CandidateProfile,
        required_skills: list[str],
        preferred_skills: list[str],
    ) -> tuple[list[str], list[str], list[str]]:
        candidate_keys = {
            cls._skill_key(skill)
            for skill in [*profile.skills, *profile.normalized_skills]
            if cls._skill_key(skill)
        }
        target_skills = cls._unique([*required_skills, *preferred_skills])
        matched = [skill for skill in target_skills if cls._skill_key(skill) in candidate_keys]
        if not target_skills:
            matched = cls._unique(profile.normalized_skills or profile.skills)
        missing_required = [
            skill for skill in required_skills if cls._skill_key(skill) not in candidate_keys
        ]
        missing_preferred = [
            skill for skill in preferred_skills if cls._skill_key(skill) not in candidate_keys
        ]
        return matched, missing_required, missing_preferred

    @classmethod
    def _parse_score(cls, result: Any) -> _ParsedScore | None:
        if not isinstance(result, dict):
            return None
        status = result.get("status")
        if status not in (None, "scored"):
            return None

        overall = cls._number(result, "overall_score", "score_total", "total_score")
        match = cls._number(result, "job_match_score", "match_score", "match_rate")
        dimensions = cls._dimension_scores(result)
        action = result.get("recommended_action", result.get("recommendation"))
        risk_tags = result.get("risk_tags", [])
        if (
            overall is None
            or match is None
            or dimensions is None
            or not isinstance(action, str)
            or not action.strip()
            or not isinstance(risk_tags, (list, tuple))
        ):
            return None
        return _ParsedScore(
            overall_score=overall,
            job_match_score=match,
            dimension_scores=dimensions,
            recommended_action=action.strip(),
            risk_tags=cls._unique([str(item) for item in risk_tags]),
        )

    @classmethod
    def _dimension_scores(cls, result: dict[str, Any]) -> dict[str, float] | None:
        source: Any = result.get("score_breakdown")
        if isinstance(source, dict) and isinstance(source.get("dimension_scores"), dict):
            source = source["dimension_scores"]
        if not isinstance(source, dict) or not all(key in source for key in DIMENSION_NAMES):
            explanation = result.get("explanation")
            source = explanation.get("dimension_scores") if isinstance(explanation, dict) else None
        if not isinstance(source, dict):
            return None

        dimensions: dict[str, float] = {}
        for key in DIMENSION_NAMES:
            value = cls._coerce_score(source.get(key))
            if value is None:
                return None
            dimensions[key] = value
        return dimensions

    @classmethod
    def _number(cls, result: dict[str, Any], *keys: str) -> float | None:
        for key in keys:
            if key in result:
                return cls._coerce_score(result[key])
        return None

    @staticmethod
    def _coerce_score(value: Any) -> float | None:
        if isinstance(value, bool):
            return None
        try:
            score = float(value)
        except (TypeError, ValueError):
            return None
        if not isfinite(score) or not 0 <= score <= 100:
            return None
        return score

    @classmethod
    def _interview_questions(
        cls,
        missing_required: list[str],
        missing_preferred: list[str],
        dimensions: dict[str, float],
        risk_tags: list[str],
    ) -> list[str]:
        questions = [
            f"请结合真实项目说明对必备技能「{skill}」的掌握情况，并提供可核验证据。"
            for skill in missing_required
        ]
        questions.extend(
            f"请说明是否具备加分技能「{skill}」及其真实应用场景。"
            for skill in missing_preferred
        )
        questions.extend(
            f"请补充说明{DIMENSION_NAMES[key]}相关经历，并提供可核验证据。"
            for key, score in dimensions.items()
            if score < LOW_DIMENSION_THRESHOLD
        )
        questions.extend(
            f"请围绕风险项「{risk}」补充可核验说明。"
            for risk in risk_tags
        )
        return cls._unique(questions)

    @classmethod
    def _unavailable_summary(
        cls,
        profile: CandidateProfile,
        knowledge: EnterpriseKnowledgeSummary,
        matched_skills: list[str],
        missing_required: list[str],
        missing_preferred: list[str],
        evidence_ids: list[str],
        must_have_passed: bool,
    ) -> JobMatchSummary:
        return JobMatchSummary(
            candidate_id=profile.candidate_id,
            overall_score=None,
            job_match_score=None,
            dimension_scores={},
            must_have_passed=must_have_passed,
            matched_skills=matched_skills,
            missing_skills=[*missing_required, *missing_preferred],
            evidence_ids=evidence_ids,
            knowledge_sources=list(knowledge.sources),
            suggested_interview_questions=cls._interview_questions(
                missing_required,
                missing_preferred,
                {},
                [],
            ),
            recommended_action=SCORING_UNAVAILABLE_ACTION,
            scoring_mode=SCORING_MODE,
            requires_review=True,
        )

    @classmethod
    def _evidence_ids(cls, profile: CandidateProfile) -> list[str]:
        return cls._unique([item.evidence_id for item in profile.evidence_items])

    @staticmethod
    def _skill_key(value: str) -> str:
        return str(value).strip().casefold()

    @classmethod
    def _unique(cls, values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            cleaned = str(value).strip()
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result


__all__ = ["CandidateEvaluationService", "CandidateEvaluationServiceProtocol"]
