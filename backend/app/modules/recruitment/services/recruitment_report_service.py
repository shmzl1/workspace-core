"""Structured HR report generation for Sprint 2.3 Agent runs."""

from __future__ import annotations

from collections import Counter

from app.agents.shared import KnowledgeSourceReference
from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    DecisionReviewSummary,
    EnterpriseKnowledgeSummary,
    HRReportSummary,
    InterviewEvaluationSummary,
    JobMatchSummary,
    RecruitmentGoal,
)
from app.modules.recruitment.services.contracts import RecruitmentReportServiceProtocol

GENERATION_MODE = "RULE_BASED_INTERMEDIATE"
REAL_INTERVIEW_STATUSES = {
    "COMPLETED",
    "EVALUATED",
    "FINISHED",
    "已完成",
    "已评价",
}
CRITICAL_PROFILE_FIELDS = (
    "skills",
    "experience_months",
    "education",
    "projects",
)
PROFILE_FIELD_NAMES = {
    "skills": "技能",
    "experience_months": "工作经验",
    "education": "教育背景",
    "projects": "项目经历",
    "project_roles": "项目职责",
    "project_technologies": "项目技术",
    "measurable_achievements": "可量化成果",
    "certificates": "证书",
    "availability": "到岗时间",
}


class RecruitmentReportService:
    """Aggregate only existing structured results into an HR review report."""

    def build_report(
        self,
        goal: RecruitmentGoal,
        job_matches: dict[int, JobMatchSummary],
        decision_reviews: dict[int, DecisionReviewSummary],
        knowledge: EnterpriseKnowledgeSummary,
        candidate_profiles: dict[int, CandidateProfile],
        interview_evaluations: dict[int, InterviewEvaluationSummary],
    ) -> HRReportSummary:
        candidate_ids = sorted(
            set(job_matches)
            | set(decision_reviews)
            | set(candidate_profiles)
            | set(interview_evaluations)
        )
        rankings = sorted(
            candidate_ids,
            key=lambda candidate_id: self._ranking_key(
                candidate_id,
                job_matches.get(candidate_id),
            ),
        )
        reviews = [
            decision_reviews[candidate_id]
            for candidate_id in rankings
            if candidate_id in decision_reviews
        ]
        sources = self._knowledge_sources(rankings, knowledge, job_matches)
        talent_gaps = self._talent_gaps(
            goal,
            rankings,
            job_matches,
            candidate_profiles,
            interview_evaluations,
        )
        next_actions = self._next_actions(
            goal,
            rankings,
            job_matches,
            decision_reviews,
            candidate_profiles,
            interview_evaluations,
        )
        return HRReportSummary(
            goal=goal,
            candidate_rankings=rankings,
            candidate_reviews=reviews,
            knowledge_sources=sources,
            talent_gaps=talent_gaps,
            next_actions=next_actions,
            requires_human_decision=True,
            generation_mode=GENERATION_MODE,
        )

    @staticmethod
    def _ranking_key(
        candidate_id: int,
        job_match: JobMatchSummary | None,
    ) -> tuple[bool, float, int]:
        score = job_match.overall_score if job_match is not None else None
        return score is None, -(score or 0.0), candidate_id

    @classmethod
    def _knowledge_sources(
        cls,
        rankings: list[int],
        knowledge: EnterpriseKnowledgeSummary,
        job_matches: dict[int, JobMatchSummary],
    ) -> list[KnowledgeSourceReference]:
        ordered_sources = list(knowledge.sources)
        for candidate_id in rankings:
            match = job_matches.get(candidate_id)
            if match is not None:
                ordered_sources.extend(match.knowledge_sources)

        seen: set[str] = set()
        result: list[KnowledgeSourceReference] = []
        for source in ordered_sources:
            source_id = source.source_id.strip()
            if source_id and source_id not in seen:
                seen.add(source_id)
                result.append(source)
        return result

    @classmethod
    def _talent_gaps(
        cls,
        goal: RecruitmentGoal,
        rankings: list[int],
        job_matches: dict[int, JobMatchSummary],
        candidate_profiles: dict[int, CandidateProfile],
        interview_evaluations: dict[int, InterviewEvaluationSummary],
    ) -> list[str]:
        gaps: list[str] = []
        evaluated_matches = [
            job_matches[candidate_id]
            for candidate_id in rankings
            if candidate_id in job_matches
        ]
        missing_skill_counts: Counter[str] = Counter()
        skill_names: dict[str, str] = {}
        for match in evaluated_matches:
            for skill in cls._unique(match.missing_skills):
                key = cls._key(skill)
                missing_skill_counts[key] += 1
                skill_names.setdefault(key, skill)

        required_keys = {cls._key(skill) for skill in goal.required_skills}
        match_count = len(evaluated_matches)
        for key in sorted(missing_skill_counts, key=lambda item: skill_names[item].casefold()):
            count = missing_skill_counts[key]
            skill = skill_names[key]
            if match_count and count == match_count:
                category = "必备技能" if key in required_keys else "技能"
                gaps.append(f"所有已匹配候选人均缺少{category}：{skill}")
            elif match_count and key in required_keys and count > match_count / 2:
                gaps.append(
                    f"多数已匹配候选人缺少必备技能：{skill}（{count}/{match_count}）"
                )

        if len(evaluated_matches) < len(rankings):
            gaps.append(
                f"{len(rankings) - len(evaluated_matches)} 名候选人缺少确定性岗位匹配结果"
            )

        missing_interview_ids = [
            candidate_id
            for candidate_id in rankings
            if not cls._has_real_interview(interview_evaluations.get(candidate_id))
        ]
        if rankings and len(missing_interview_ids) == len(rankings):
            gaps.append("当前候选人整体缺少真实结构化面试评价")
        elif missing_interview_ids:
            gaps.append(f"{len(missing_interview_ids)} 名候选人缺少真实结构化面试评价")

        profiles = [
            candidate_profiles[candidate_id]
            for candidate_id in rankings
            if candidate_id in candidate_profiles
        ]
        for field in CRITICAL_PROFILE_FIELDS:
            missing_count = sum(cls._profile_field_missing(profile, field) for profile in profiles)
            if profiles and missing_count > len(profiles) / 2:
                gaps.append(
                    f"候选人画像整体缺少关键字段：{PROFILE_FIELD_NAMES[field]}"
                )
        return cls._unique(gaps)

    @classmethod
    def _next_actions(
        cls,
        goal: RecruitmentGoal,
        rankings: list[int],
        job_matches: dict[int, JobMatchSummary],
        decision_reviews: dict[int, DecisionReviewSummary],
        candidate_profiles: dict[int, CandidateProfile],
        interview_evaluations: dict[int, InterviewEvaluationSummary],
    ) -> list[str]:
        actions: list[str] = []
        for candidate_id in rankings:
            match = job_matches.get(candidate_id)
            review = decision_reviews.get(candidate_id)
            profile = candidate_profiles.get(candidate_id)
            has_high_finding = bool(
                review
                and any(finding.severity == "HIGH" for finding in review.findings)
            )
            confidence_low = bool(
                review is None
                or review.confidence is None
                or review.confidence < goal.confidence_threshold
            )
            score_unavailable = match is None or match.overall_score is None
            if score_unavailable or confidence_low or has_high_finding:
                actions.append(f"对候选人 #{candidate_id} 进行人工复核")

            if not cls._has_real_interview(interview_evaluations.get(candidate_id)):
                actions.append(f"为候选人 #{candidate_id} 安排或补充结构化面试")

            if profile is not None:
                missing_fields = cls._profile_missing_fields(profile)
                if missing_fields:
                    labels = [PROFILE_FIELD_NAMES[field] for field in missing_fields]
                    actions.append(
                        f"请候选人 #{candidate_id} 补充简历信息：{'、'.join(labels)}"
                    )

            meets_thresholds = bool(
                match is not None
                and match.overall_score is not None
                and match.overall_score >= goal.score_threshold
                and match.must_have_passed is True
                and review is not None
                and review.confidence is not None
                and review.confidence >= goal.confidence_threshold
                and not has_high_finding
            )
            if meets_thresholds:
                actions.append(f"将候选人 #{candidate_id} 纳入下一步人工筛选")

        actions.append("由 HR 对结构化结果完成最终复核与决定")
        return cls._unique(actions)

    @classmethod
    def _profile_missing_fields(cls, profile: CandidateProfile) -> list[str]:
        declared = set(profile.missing_fields)
        return [
            field
            for field in PROFILE_FIELD_NAMES
            if field in declared or cls._profile_field_missing(profile, field)
        ]

    @classmethod
    def _profile_field_missing(cls, profile: CandidateProfile, field: str) -> bool:
        value = getattr(profile, field)
        if value is None:
            return True
        if isinstance(value, str):
            return not value.strip()
        if isinstance(value, (list, tuple, set, dict)):
            return not value
        return False

    @staticmethod
    def _has_real_interview(
        evaluation: InterviewEvaluationSummary | None,
    ) -> bool:
        if evaluation is None or not evaluation.conclusion.strip():
            return False
        status = evaluation.status.strip()
        return status.upper() in REAL_INTERVIEW_STATUSES or status in REAL_INTERVIEW_STATUSES

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


__all__ = ["RecruitmentReportService", "RecruitmentReportServiceProtocol"]
