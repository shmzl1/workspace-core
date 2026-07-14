"""Rule-based decision review for Sprint 2.3 Agent runs."""

from __future__ import annotations

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewFinding,
    DecisionReviewSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)
from app.modules.recruitment.services.contracts import DecisionReviewServiceProtocol

REVIEW_MODE = "RULE_BASED_INTERMEDIATE"
PROFILE_FIELDS = (
    "skills",
    "experience_months",
    "education",
    "projects",
    "project_roles",
    "project_technologies",
    "measurable_achievements",
    "certificates",
    "availability",
)
CORE_PROFILE_FIELDS = {"skills", "experience_months"}
REAL_INTERVIEW_STATUSES = {
    "COMPLETED",
    "EVALUATED",
    "FINISHED",
    "已完成",
    "已评价",
}


class DecisionReviewService:
    """Review evidence and thresholds without changing deterministic scores."""

    def review(
        self,
        goal: RecruitmentGoal,
        profile: CandidateProfile,
        job_match: JobMatchSummary,
        interview_evaluation: InterviewEvaluationSummary | None = None,
    ) -> DecisionReviewSummary:
        findings: list[DecisionReviewFinding] = []
        disagreements: list[str] = []
        key_skills = self._unique(
            [
                *goal.required_skills,
                *goal.preferred_skills,
                *job_match.matched_skills,
                *job_match.missing_skills,
            ]
        )

        matched_keys = {self._key(skill) for skill in job_match.matched_skills}
        missing_keys = {self._key(skill) for skill in job_match.missing_skills}
        evidence_ids = {item.evidence_id for item in profile.evidence_items}
        referenced_evidence_ids = set(job_match.evidence_ids)
        valid_references = evidence_ids & referenced_evidence_ids
        supported_skill_keys = self._supported_skill_keys(profile, valid_references)
        supported_key_skills = [
            skill
            for skill in key_skills
            if self._key(skill) in matched_keys and self._key(skill) in supported_skill_keys
        ]
        evidence_coverage = (
            len(supported_key_skills) / len(key_skills) * 100
            if key_skills
            else 100.0
        )

        missing_profile_fields = self._missing_profile_fields(profile)
        present_profile_fields = len(PROFILE_FIELDS) - len(
            [field for field in PROFILE_FIELDS if field in missing_profile_fields]
        )
        profile_completeness = present_profile_fields / len(PROFILE_FIELDS) * 100
        score_available = bool(
            job_match.overall_score is not None
            and job_match.job_match_score is not None
            and job_match.scoring_mode == "DETERMINISTIC_HUMAN_ONLY"
        )
        interview_available = self._has_real_interview(interview_evaluation)
        confidence = round(
            min(
                100.0,
                max(
                    0.0,
                    0.4 * evidence_coverage
                    + 0.3 * profile_completeness
                    + 0.2 * (100.0 if score_available else 0.0)
                    + 0.1 * (100.0 if interview_available else 0.0),
                ),
            ),
            2,
        )

        if not score_available:
            findings.append(
                self._finding(
                    "DETERMINISTIC_SCORE_UNAVAILABLE",
                    "HIGH",
                    "确定性评分不可用，当前结论不能作为自动决策依据。",
                )
            )

        required_missing = [
            skill
            for skill in goal.required_skills
            if self._key(skill) in missing_keys
        ]
        if job_match.must_have_passed is False:
            summary = (
                f"必备技能未通过：{'、'.join(required_missing)}。"
                if required_missing
                else "必备技能检查未通过，需人工核对岗位要求与候选人材料。"
            )
            findings.append(self._finding("REQUIRED_SKILL_MISSING", "HIGH", summary))

        unsupported_matched = [
            skill
            for skill in job_match.matched_skills
            if self._key(skill) not in supported_skill_keys
        ]
        invalid_evidence_ids = [
            evidence_id
            for evidence_id in job_match.evidence_ids
            if evidence_id not in evidence_ids
        ]
        if unsupported_matched or invalid_evidence_ids:
            details: list[str] = []
            if unsupported_matched:
                details.append(f"缺少支持证据的匹配技能：{'、'.join(unsupported_matched)}")
            if invalid_evidence_ids:
                details.append("岗位匹配结果引用了画像中不存在的证据编号")
            severity = "HIGH" if unsupported_matched and not supported_key_skills else "MEDIUM"
            findings.append(
                self._finding(
                    "EVIDENCE_GAP",
                    severity,
                    "；".join(details) + "。",
                )
            )

        if missing_profile_fields:
            severity = (
                "HIGH"
                if CORE_PROFILE_FIELDS & set(missing_profile_fields)
                else "MEDIUM"
            )
            findings.append(
                self._finding(
                    "PROFILE_INCOMPLETE",
                    severity,
                    f"候选人画像仍缺少字段：{'、'.join(missing_profile_fields)}。",
                )
            )

        if not interview_available:
            findings.append(
                self._finding(
                    "INTERVIEW_DATA_MISSING",
                    "MEDIUM",
                    "缺少真实结构化面试评价，未生成面试能力结论。",
                )
            )

        if score_available and job_match.overall_score is not None:
            if job_match.overall_score < goal.score_threshold:
                findings.append(
                    self._finding(
                        "SCORE_BELOW_THRESHOLD",
                        "MEDIUM",
                        (
                            f"确定性评分 {job_match.overall_score:g} 低于当前评分阈值 "
                            f"{goal.score_threshold:g}。"
                        ),
                    )
                )

        if confidence < goal.confidence_threshold:
            findings.append(
                self._finding(
                    "CONFIDENCE_BELOW_THRESHOLD",
                    "HIGH",
                    (
                        f"审查可信度 {confidence:g} 低于当前可信度阈值 "
                        f"{goal.confidence_threshold:g}。"
                    ),
                )
            )

        inconsistency_reasons = self._score_evidence_inconsistencies(
            profile,
            job_match,
            required_missing,
            matched_keys,
            missing_keys,
            supported_skill_keys,
        )
        if inconsistency_reasons:
            summary = "；".join(inconsistency_reasons) + "。"
            findings.append(
                self._finding(
                    "SCORE_EVIDENCE_INCONSISTENCY",
                    "HIGH",
                    summary,
                )
            )
            disagreements.append(summary)

        has_high_risk = any(finding.severity == "HIGH" for finding in findings)
        if has_high_risk or confidence < goal.confidence_threshold:
            recommended_action = "建议人工复核"
        elif not interview_available:
            recommended_action = "建议安排或补充结构化面试"
        elif findings:
            recommended_action = "建议人工复核"
        else:
            recommended_action = "建议进入下一步人工筛选"

        return DecisionReviewSummary(
            candidate_id=profile.candidate_id,
            confidence=confidence,
            findings=findings,
            risk_tags=self._unique([finding.code for finding in findings]),
            agent_disagreements=disagreements,
            deterministic_score_preserved=True,
            recommended_action=recommended_action,
            review_mode=REVIEW_MODE,
        )

    @staticmethod
    def _finding(code: str, severity: str, summary: str) -> DecisionReviewFinding:
        return DecisionReviewFinding(
            code=code,
            severity=severity,
            summary=summary,
            evidence_ids=[],
            requires_human_review=True,
        )

    @classmethod
    def _supported_skill_keys(
        cls,
        profile: CandidateProfile,
        valid_references: set[str],
    ) -> set[str]:
        evidence_capabilities = {
            cls._key(item.capability)
            for item in profile.evidence_items
            if item.evidence_id in valid_references and item.supports is not False
        }
        supported = set(evidence_capabilities)
        for index, raw_skill in enumerate(profile.skills):
            raw_key = cls._key(raw_skill)
            if raw_key not in evidence_capabilities:
                continue
            supported.add(raw_key)
            if index < len(profile.normalized_skills):
                supported.add(cls._key(profile.normalized_skills[index]))
        return supported

    @classmethod
    def _missing_profile_fields(cls, profile: CandidateProfile) -> list[str]:
        missing = {
            field
            for field in PROFILE_FIELDS
            if not cls._has_value(getattr(profile, field))
        }
        missing.update(field for field in profile.missing_fields if field in PROFILE_FIELDS)
        return [field for field in PROFILE_FIELDS if field in missing]

    @staticmethod
    def _has_value(value: object) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (list, tuple, set, dict)):
            return bool(value)
        return True

    @staticmethod
    def _has_real_interview(
        evaluation: InterviewEvaluationSummary | None,
    ) -> bool:
        if evaluation is None or not evaluation.conclusion.strip():
            return False
        status = evaluation.status.strip()
        return status.upper() in REAL_INTERVIEW_STATUSES or status in REAL_INTERVIEW_STATUSES

    @classmethod
    def _score_evidence_inconsistencies(
        cls,
        profile: CandidateProfile,
        job_match: JobMatchSummary,
        required_missing: list[str],
        matched_keys: set[str],
        missing_keys: set[str],
        supported_skill_keys: set[str],
    ) -> list[str]:
        reasons: list[str] = []
        profile_skill_keys = {
            cls._key(skill)
            for skill in [*profile.skills, *profile.normalized_skills]
        }
        unknown_claims = [
            skill
            for skill in job_match.matched_skills
            if cls._key(skill) not in profile_skill_keys
        ]
        if unknown_claims:
            reasons.append(f"匹配结论包含画像未声明的技能：{'、'.join(unknown_claims)}")
        if matched_keys & missing_keys:
            reasons.append("同一技能同时出现在已匹配和缺失列表")
        if job_match.must_have_passed is True and required_missing:
            reasons.append("必备条件通过结论与缺失的必备技能不一致")
        if job_match.overall_score is not None and job_match.job_match_score is None:
            reasons.append("存在综合评分但缺少岗位匹配评分")
        if job_match.matched_skills and not (
            matched_keys & supported_skill_keys
        ):
            reasons.append("存在技能匹配结论但没有任何匹配技能获得证据支持")
        return cls._unique(reasons)

    @staticmethod
    def _key(value: str) -> str:
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


__all__ = ["DecisionReviewService", "DecisionReviewServiceProtocol"]
