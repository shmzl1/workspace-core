"""Local structured and keyword knowledge fallback for Sprint 2.2."""

import re
from datetime import date
from typing import Any

from app.agents.shared import KnowledgeSourceReference
from app.agents.workflows.recruitment_decision.contracts import (
    EnterpriseKnowledgeSummary,
    JobRequirementItem,
    JobRubric,
    RecruitmentRunContext,
)

INTERVIEW_CRITERIA = ("技术能力", "项目能力", "沟通表达", "问题解决能力")
RISK_RULES = ("必备技能缺失需要人工复核", "经验低于岗位最低要求需要补充验证", "无证据能力不得标记为明确具备")
RULES_VERSION = "recruitment-rules-v1"
RULES_EFFECTIVE_DATE = date(2026, 7, 10)


class RecruitmentKnowledgeService:
    """Build and rank current sources without ChromaDB, embeddings or LLM."""

    def retrieve(self, context: RecruitmentRunContext) -> tuple[EnterpriseKnowledgeSummary, JobRubric]:
        query_text = " ".join(
            [
                context.job.job_title,
                context.job.department,
                *context.request.goal.required_skills,
                *context.request.goal.preferred_skills,
            ]
        )
        documents = self._documents(context)
        ranked = sorted(
            documents,
            key=lambda document: self._relevance(query_text, document),
            reverse=True,
        )
        sources = [self._source(document, self._relevance(query_text, document)) for document in ranked]
        job_source_id = f"job:{context.job.job_code}"
        rule_source_id = f"rules:{RULES_VERSION}"
        requirements = [
            JobRequirementItem(
                requirement_id=f"required-skill-{index}",
                category="REQUIRED_SKILL",
                description=skill,
                required=True,
                source_ids=[job_source_id],
            )
            for index, skill in enumerate(context.job.required_skills, 1)
        ]
        requirements.extend(
            JobRequirementItem(
                requirement_id=f"preferred-skill-{index}",
                category="PREFERRED_SKILL",
                description=skill,
                required=False,
                source_ids=[job_source_id],
            )
            for index, skill in enumerate(context.job.preferred_skills, 1)
        )
        requirements.append(
            JobRequirementItem(
                requirement_id="minimum-experience",
                category="MINIMUM_EXPERIENCE",
                description=f"至少 {context.job.min_experience_months} 个月相关经验",
                required=True,
                source_ids=[job_source_id],
            )
        )
        requirements.extend(
            JobRequirementItem(
                requirement_id=f"interview-criterion-{index}",
                category="INTERVIEW_CRITERION",
                description=criterion,
                required=False,
                source_ids=[rule_source_id],
            )
            for index, criterion in enumerate(INTERVIEW_CRITERIA, 1)
        )
        rubric = JobRubric(
            job_id=context.job.job_id,
            version=context.job.source_version,
            requirements=requirements,
        )
        summary = EnterpriseKnowledgeSummary(
            job_id=context.job.job_id,
            job_code=context.job.job_code,
            standard_version=context.job.source_version,
            effective_date=context.job.effective_date,
            required_skills=context.job.required_skills,
            preferred_skills=context.job.preferred_skills,
            min_experience_months=context.job.min_experience_months,
            interview_criteria=list(INTERVIEW_CRITERIA),
            risk_rules=list(RISK_RULES),
            retrieval_mode="LOCAL_HYBRID_FALLBACK",
            sources=sources,
        )
        return summary, rubric

    @staticmethod
    def _documents(context: RecruitmentRunContext) -> list[dict[str, Any]]:
        return [
            {
                "source_id": f"job:{context.job.job_code}",
                "title": f"{context.job.job_title}岗位标准",
                "document_type": "JOB_STANDARD",
                "department": context.job.department,
                "job_code": context.job.job_code,
                "version": context.job.source_version,
                "effective_date": context.job.effective_date,
                "text": (
                    f"必备技能：{'、'.join(context.job.required_skills) or '未配置'}；"
                    f"加分技能：{'、'.join(context.job.preferred_skills) or '未配置'}；"
                    f"最低经验：{context.job.min_experience_months}个月。"
                ),
                "metadata_score": 1.0,
            },
            {
                "source_id": f"goal:job-{context.job.job_id}",
                "title": f"{context.job.job_title}当前招聘目标",
                "document_type": "HIRING_GOAL",
                "department": context.job.department,
                "job_code": context.job.job_code,
                "version": "goal-request-v1",
                "effective_date": date.today(),
                "text": (
                    f"目标人数：{context.request.goal.target_headcount}；"
                    f"紧急程度：{context.request.goal.urgency.value}；"
                    f"评分阈值：{context.request.goal.score_threshold}；"
                    f"可信度阈值：{context.request.goal.confidence_threshold}。"
                ),
                "metadata_score": 1.0,
            },
            {
                "source_id": f"rules:{RULES_VERSION}",
                "title": "招聘面试与风险规则",
                "document_type": "RECRUITMENT_RULES",
                "department": None,
                "job_code": None,
                "version": RULES_VERSION,
                "effective_date": RULES_EFFECTIVE_DATE,
                "text": f"面试标准：{'、'.join(INTERVIEW_CRITERIA)}；风险规则：{'；'.join(RISK_RULES)}。",
                "metadata_score": 0.7,
            },
        ]

    @classmethod
    def _relevance(cls, query: str, document: dict[str, Any]) -> float:
        query_tokens = cls._tokens(query)
        document_tokens = cls._tokens(str(document["text"]))
        overlap = len(query_tokens & document_tokens) / max(1, len(query_tokens))
        return round(min(1.0, float(document["metadata_score"]) * 0.7 + overlap * 0.3), 4)

    @staticmethod
    def _tokens(value: str) -> set[str]:
        return {
            token.casefold()
            for token in re.findall(r"[A-Za-z0-9+#.]+|[\u4e00-\u9fff]{2,}", value)
            if token.strip()
        }

    @staticmethod
    def _source(document: dict[str, Any], relevance: float) -> KnowledgeSourceReference:
        return KnowledgeSourceReference(
            source_id=document["source_id"],
            title=document["title"],
            document_type=document["document_type"],
            department=document["department"],
            job_code=document["job_code"],
            version=document["version"],
            effective_from=document["effective_date"],
            effective_date=document["effective_date"],
            excerpt=str(document["text"])[:240],
            relevance=relevance,
        )
