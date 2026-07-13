"""Unified recruitment knowledge entry with explicit local fallback."""

from app.agents.workflows.recruitment_decision.contracts import (
    EnterpriseKnowledgeSummary,
    JobRubric,
    RecruitmentRunContext,
)
from app.modules.recruitment.services.local_fallback_knowledge_service import (
    LocalFallbackRecruitmentKnowledgeService,
)
from app.modules.recruitment.services.recruitment_knowledge_adapter import RecruitmentKnowledgeAdapter
from app.rag.errors import (
    EmbeddingProviderError,
    KnowledgeBaseError,
    KnowledgeMappingError,
)
from app.rag.retrieval.gateway import DisabledRetrievalGateway, RetrievalGateway
from app.rag.schemas import RetrievalFilter, RetrievalQuery


class RecruitmentKnowledgeService:
    def __init__(
        self,
        retrieval_gateway: RetrievalGateway | None = None,
        fallback_service: LocalFallbackRecruitmentKnowledgeService | None = None,
        knowledge_adapter: RecruitmentKnowledgeAdapter | None = None,
    ) -> None:
        self.retrieval_gateway = retrieval_gateway or DisabledRetrievalGateway()
        self.fallback_service = fallback_service or LocalFallbackRecruitmentKnowledgeService()
        self.knowledge_adapter = knowledge_adapter or RecruitmentKnowledgeAdapter()

    async def retrieve(
        self,
        context: RecruitmentRunContext,
    ) -> tuple[EnterpriseKnowledgeSummary, JobRubric]:
        query = RetrievalQuery(
            text=" ".join([
                context.job.job_title,
                *context.request.goal.required_skills,
                *context.request.goal.preferred_skills,
            ]),
            filters=RetrievalFilter(
                document_types=["JOB_STANDARD", "RECRUITMENT_RULES", "INTERVIEW_STANDARD"],
                departments=[context.job.department],
                job_codes=[context.job.job_code],
                effective_on=context.job.effective_date,
            ),
            limit=6,
        )
        try:
            result = await self.retrieval_gateway.retrieve(query)
            return self.knowledge_adapter.to_domain(context, result)
        except KnowledgeMappingError:
            warning = "RAG_MAPPING_FAILED_LOCAL_FALLBACK"
        except EmbeddingProviderError as exc:
            warning = exc.code
        except KnowledgeBaseError:
            warning = "RAG_UNAVAILABLE_LOCAL_FALLBACK"
        except (ValueError, TypeError):
            warning = "RAG_RESULT_INVALID_LOCAL_FALLBACK"

        summary, rubric = await self.fallback_service.retrieve(context)
        return summary.model_copy(update={"warnings": [warning]}), rubric
