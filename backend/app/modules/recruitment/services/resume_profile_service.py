"""Deterministic Sprint 2.2 candidate-profile extraction Service."""

import re

from app.agents.workflows.recruitment_decision.contracts import (
    CandidateProfile,
    RecruitmentCandidateContext,
    ResumeEvidenceItem,
)

MAX_EVIDENCE_EXCERPT = 160

SKILL_ALIASES = {
    "vue.js": "Vue",
    "vuejs": "Vue",
    "vue 3": "Vue",
    "typescript": "TypeScript",
    "javascript": "JavaScript",
    "python": "Python",
    "fastapi": "FastAPI",
    "postgres": "PostgreSQL",
    "postgresql": "PostgreSQL",
    "tailwindcss": "Tailwind CSS",
    "tailwind css": "Tailwind CSS",
    "vite": "Vite",
}


class ResumeProfileService:
    """Extract facts only from whitelisted structured fields and safe excerpts."""

    def extract(self, candidate: RecruitmentCandidateContext) -> CandidateProfile:
        skills = self._unique(candidate.skills)
        normalized_skills = self._unique([self._normalize_skill(skill) for skill in skills])
        evidence: list[ResumeEvidenceItem] = []

        for index, skill in enumerate(skills, 1):
            excerpt, section, confidence = self._skill_evidence(skill, candidate.resume_excerpt)
            evidence.append(
                ResumeEvidenceItem(
                    evidence_id=f"candidate-{candidate.candidate_id}-skill-{index}",
                    capability=skill,
                    excerpt=excerpt,
                    source_section=section,
                    supports=True,
                    confidence=confidence,
                )
            )

        if candidate.experience_months is not None:
            evidence.append(
                ResumeEvidenceItem(
                    evidence_id=f"candidate-{candidate.candidate_id}-experience",
                    capability="工作经验",
                    excerpt=f"结构化经验字段：{candidate.experience_months} 个月",
                    source_section="structured_experience",
                    supports=True,
                    confidence=0.95,
                )
            )

        evidence.extend(self._list_evidence(candidate.candidate_id, "education", "教育背景", candidate.education))
        evidence.extend(self._list_evidence(candidate.candidate_id, "project", "项目经历", candidate.projects))
        evidence.extend(
            self._list_evidence(
                candidate.candidate_id,
                "achievement",
                "可量化成果",
                candidate.measurable_achievements,
            )
        )

        missing_fields = [
            field_name
            for field_name, value in (
                ("skills", skills),
                ("experience_months", candidate.experience_months),
                ("education", candidate.education),
                ("projects", candidate.projects),
                ("project_roles", candidate.project_roles),
                ("project_technologies", candidate.project_technologies),
                ("measurable_achievements", candidate.measurable_achievements),
                ("certificates", candidate.certificates),
                ("availability", candidate.availability),
            )
            if value is None or value == [] or value == ""
        ]

        return CandidateProfile(
            candidate_id=candidate.candidate_id,
            skills=skills,
            normalized_skills=normalized_skills,
            experience_months=candidate.experience_months,
            education=self._unique(candidate.education),
            projects=self._unique(candidate.projects),
            project_roles=self._unique(candidate.project_roles),
            project_technologies=self._unique(candidate.project_technologies),
            measurable_achievements=self._unique(candidate.measurable_achievements),
            certificates=self._unique(candidate.certificates),
            availability=candidate.availability,
            missing_fields=missing_fields,
            evidence_items=evidence,
            extraction_mode="STRUCTURED_DATABASE_FALLBACK",
            fallback_used=True,
        )

    @staticmethod
    def _unique(values: list[str]) -> list[str]:
        seen: set[str] = set()
        result: list[str] = []
        for value in values:
            cleaned = str(value).strip()
            key = cleaned.casefold()
            if cleaned and key not in seen:
                seen.add(key)
                result.append(cleaned)
        return result

    @staticmethod
    def _normalize_skill(skill: str) -> str:
        cleaned = skill.strip()
        return SKILL_ALIASES.get(cleaned.casefold(), cleaned)

    @staticmethod
    def _skill_evidence(skill: str, resume_excerpt: str | None) -> tuple[str, str, float]:
        if resume_excerpt:
            for segment in re.split(r"[。！？!?；;\r\n]+", resume_excerpt):
                cleaned = segment.strip()
                if skill.casefold() in cleaned.casefold():
                    return cleaned[:MAX_EVIDENCE_EXCERPT], "resume_excerpt", 0.95
        return f"结构化技能字段：{skill}", "structured_skills", 0.9

    @staticmethod
    def _list_evidence(
        candidate_id: int,
        key: str,
        capability: str,
        values: list[str],
    ) -> list[ResumeEvidenceItem]:
        return [
            ResumeEvidenceItem(
                evidence_id=f"candidate-{candidate_id}-{key}-{index}",
                capability=capability,
                excerpt=f"结构化{capability}字段：{value}"[:MAX_EVIDENCE_EXCERPT],
                source_section=f"structured_{key}",
                supports=True,
                confidence=0.9,
            )
            for index, value in enumerate(values, 1)
        ]
