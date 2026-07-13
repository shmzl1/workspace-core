"""Pure adapter from generic retrieval contracts to recruitment domain contracts."""

from typing import Any

from app.agents.shared import KnowledgeSourceReference
from app.agents.workflows.recruitment_decision.contracts import (
    EnterpriseKnowledgeSummary,
    JobRequirementItem,
    JobRubric,
    RecruitmentRunContext,
)
from app.rag.errors import KnowledgeMappingError
from app.rag.schemas import RetrievalResult


class RecruitmentKnowledgeAdapter:
    def to_domain(
        self,
        context: RecruitmentRunContext,
        result: RetrievalResult,
    ) -> tuple[EnterpriseKnowledgeSummary, JobRubric]:
        if not result.hits:
            raise KnowledgeMappingError("检索结果没有可映射的真实知识来源。")

        attributes = [hit.chunk.attributes for hit in result.hits]
        required_present = any("required_skills" in item for item in attributes)
        experience_present = any("min_experience_months" in item for item in attributes)
        if not required_present or not experience_present:
            raise KnowledgeMappingError("检索结果缺少岗位必备技能或最低经验等关键结构化知识。")

        required_skills = self._strings(attributes, "required_skills")
        preferred_skills = self._strings(attributes, "preferred_skills")
        interview_criteria = self._strings(attributes, "interview_criteria")
        risk_rules = self._strings(attributes, "risk_rules")
        min_experience = self._minimum_experience(attributes)
        sources = [self._source(hit) for hit in result.hits]
        source_ids = [source.source_id for source in sources]
        requirements = [
            JobRequirementItem(
                requirement_id=f"required-skill-{index}", category="REQUIRED_SKILL",
                description=skill, required=True, source_ids=source_ids,
            )
            for index, skill in enumerate(required_skills, 1)
        ]
        requirements.extend(
            JobRequirementItem(
                requirement_id=f"preferred-skill-{index}", category="PREFERRED_SKILL",
                description=skill, required=False, source_ids=source_ids,
            )
            for index, skill in enumerate(preferred_skills, 1)
        )
        requirements.append(JobRequirementItem(
            requirement_id="minimum-experience", category="MINIMUM_EXPERIENCE",
            description=f"至少 {min_experience} 个月相关经验", required=True, source_ids=source_ids,
        ))
        requirements.extend(
            JobRequirementItem(
                requirement_id=f"interview-criterion-{index}", category="INTERVIEW_CRITERION",
                description=item, required=False, source_ids=source_ids,
            )
            for index, item in enumerate(interview_criteria, 1)
        )
        return (
            EnterpriseKnowledgeSummary(
                job_id=context.job.job_id,
                job_code=context.job.job_code,
                standard_version=context.job.source_version,
                effective_date=context.job.effective_date,
                required_skills=required_skills,
                preferred_skills=preferred_skills,
                min_experience_months=min_experience,
                interview_criteria=interview_criteria,
                risk_rules=risk_rules,
                retrieval_mode=result.mode,
                sources=sources,
            ),
            JobRubric(job_id=context.job.job_id, version=context.job.source_version, requirements=requirements),
        )

    @staticmethod
    def _strings(attributes: list[dict[str, Any]], key: str) -> list[str]:
        values: list[str] = []
        for item in attributes:
            raw = item.get(key)
            if isinstance(raw, (list, tuple)):
                values.extend(str(value).strip() for value in raw if str(value).strip())
        return list(dict.fromkeys(values))

    @staticmethod
    def _minimum_experience(attributes: list[dict[str, Any]]) -> int:
        for item in attributes:
            if "min_experience_months" not in item:
                continue
            try:
                value = int(item["min_experience_months"])
            except (TypeError, ValueError) as exc:
                raise KnowledgeMappingError("最低经验字段不是有效整数。") from exc
            if value < 0:
                raise KnowledgeMappingError("最低经验字段不能为负数。")
            return value
        raise KnowledgeMappingError("检索结果缺少最低经验字段。")

    @staticmethod
    def _source(hit: Any) -> KnowledgeSourceReference:
        source = hit.chunk.source
        return KnowledgeSourceReference(
            source_id=source.source_id,
            title=source.title,
            document_type=source.document_type,
            department=source.department,
            job_code=source.job_code,
            version=source.version,
            effective_from=source.effective_from,
            effective_to=source.effective_to,
            effective_date=source.effective_from,
            excerpt=hit.chunk.text[:240],
            relevance=hit.relevance,
        )
