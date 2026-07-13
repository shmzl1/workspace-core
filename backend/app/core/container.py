"""Application-level assembly for optional integrations and Agent tools."""

from dataclasses import dataclass
from functools import lru_cache

from pydantic import BaseModel

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.shared import (
    DisabledModelGateway,
    ModelGateway,
    ModelGatewayStatus,
    NotImplementedModelGateway,
)
from app.agents.tools.knowledge_tools import EnterpriseKnowledgeTool
from app.agents.tools.recruitment_tools import (
    CandidateEvaluationTool,
    CandidateProfileTool,
    DecisionReviewTool,
    RecruitmentReportTool,
)
from app.core.config import Settings, get_settings
from app.modules.recruitment.services import (
    LocalFallbackRecruitmentKnowledgeService,
    RecruitmentKnowledgeAdapter,
    RecruitmentKnowledgeService,
)
from app.rag import (
    DisabledKnowledgeBaseLifecycle,
    DisabledRetrievalGateway,
    KnowledgeBaseLifecycle,
    KnowledgeBaseStatus,
    NotImplementedKnowledgeBaseLifecycle,
    NotImplementedRetrievalGateway,
    RetrievalGateway,
    KnowledgeBaseError,
)


class IntegrationStatus(BaseModel):
    overall_mode: str
    llm: ModelGatewayStatus
    rag: KnowledgeBaseStatus


@dataclass
class ApplicationContainer:
    settings: Settings
    model_gateway: ModelGateway
    retrieval_gateway: RetrievalGateway
    knowledge_lifecycle: KnowledgeBaseLifecycle
    recruitment_knowledge_service: RecruitmentKnowledgeService
    recruitment_runner_dependencies: RecruitmentRunnerDependencies

    async def startup(self) -> None:
        if self.settings.rag_enabled and self.settings.rag_auto_initialize:
            try:
                await self.knowledge_lifecycle.initialize()
            except KnowledgeBaseError:
                return None

    async def shutdown(self) -> None:
        for component in (self.model_gateway, self.retrieval_gateway, self.knowledge_lifecycle):
            try:
                await component.aclose()
            except Exception:
                continue

    async def get_integration_status(self) -> IntegrationStatus:
        llm = await self.model_gateway.get_status()
        rag = await self.knowledge_lifecycle.get_status()
        overall_mode = "OK" if llm.mode in {"DISABLED", "READY"} and rag.mode in {"DISABLED", "READY"} else "DEGRADED"
        return IntegrationStatus(overall_mode=overall_mode, llm=llm, rag=rag)


def _build_application_container(settings: Settings) -> ApplicationContainer:
    model_gateway: ModelGateway
    if settings.llm_enabled:
        model_gateway = NotImplementedModelGateway(
            settings.llm_provider,
            settings.openai_model or None,
            configured=settings.llm_configured,
        )
    else:
        model_gateway = DisabledModelGateway(settings.llm_provider)

    retrieval_gateway: RetrievalGateway
    knowledge_lifecycle: KnowledgeBaseLifecycle
    if settings.rag_enabled:
        retrieval_gateway = NotImplementedRetrievalGateway(
            settings.chroma_collection_name,
            configured=settings.rag_configured,
        )
        knowledge_lifecycle = NotImplementedKnowledgeBaseLifecycle(
            settings.chroma_collection_name,
            configured=settings.rag_configured,
        )
    else:
        retrieval_gateway = DisabledRetrievalGateway(settings.chroma_collection_name)
        knowledge_lifecycle = DisabledKnowledgeBaseLifecycle(settings.chroma_collection_name)

    knowledge_service = RecruitmentKnowledgeService(
        retrieval_gateway=retrieval_gateway,
        fallback_service=LocalFallbackRecruitmentKnowledgeService(),
        knowledge_adapter=RecruitmentKnowledgeAdapter(),
    )
    dependencies = RecruitmentRunnerDependencies(
        knowledge_tool=EnterpriseKnowledgeTool(knowledge_service),
        profile_tool=CandidateProfileTool(),
        candidate_evaluation_tool=CandidateEvaluationTool(),
        decision_review_tool=DecisionReviewTool(),
        report_tool=RecruitmentReportTool(),
        model_gateway=model_gateway,
    )
    return ApplicationContainer(
        settings=settings,
        model_gateway=model_gateway,
        retrieval_gateway=retrieval_gateway,
        knowledge_lifecycle=knowledge_lifecycle,
        recruitment_knowledge_service=knowledge_service,
        recruitment_runner_dependencies=dependencies,
    )


@lru_cache(maxsize=1)
def get_application_container() -> ApplicationContainer:
    return _build_application_container(get_settings())


def reset_application_container() -> None:
    get_application_container.cache_clear()
