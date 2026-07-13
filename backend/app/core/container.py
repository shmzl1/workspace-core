"""Application-level assembly for optional integrations and Agent tools."""

from dataclasses import dataclass
from functools import lru_cache

from pydantic import BaseModel

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.runtime.run_store import AgentRunStore
from app.agents.shared import (
    DisabledModelGateway,
    ModelGateway,
    ModelGatewayStatus,
    NotImplementedModelGateway,
    OpenAICompatibleModelGateway,
)
from app.agents.tools.knowledge_tools import EnterpriseKnowledgeTool
from app.agents.tools.recruitment_tools import (
    CandidateEvaluationTool,
    CandidateProfileTool,
    DecisionReviewTool,
    RecruitmentReportTool,
)
from app.core.config import Settings, get_settings
from app.core.database import SessionLocal
from app.modules.agent_runtime.service import PostgreSQLAgentRunStore
from app.modules.recruitment.services import (
    LocalFallbackRecruitmentKnowledgeService,
    RecruitmentKnowledgeAdapter,
    RecruitmentKnowledgeService,
)
from app.rag import (
    ChromaKnowledgeBaseLifecycle,
    ChromaRetrievalGateway,
    ChromaVectorStore,
    DisabledKnowledgeBaseLifecycle,
    DisabledRetrievalGateway,
    KnowledgeBaseLifecycle,
    KnowledgeBaseStatus,
    NotImplementedKnowledgeBaseLifecycle,
    NotImplementedRetrievalGateway,
    RetrievalGateway,
    KnowledgeBaseRuntimeState,
    EmbeddingClient,
    OpenAICompatibleEmbeddingClient,
    VolcengineMultimodalEmbeddingClient,
)
from app.rag.ingestion import LocalKnowledgeLoader, StructuredKnowledgeSplitter


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
    agent_run_store: AgentRunStore

    async def startup(self) -> None:
        await self.agent_run_store.recover_interrupted_runs()
        if self.settings.rag_enabled and self.settings.rag_auto_initialize:
            try:
                await self.knowledge_lifecycle.initialize()
            except Exception:
                return None

    async def shutdown(self) -> None:
        for component in (
            self.model_gateway,
            self.retrieval_gateway,
            self.knowledge_lifecycle,
            self.agent_run_store,
        ):
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
        if settings.llm_configured:
            model_gateway = OpenAICompatibleModelGateway(
                provider=settings.llm_provider,
                base_url=settings.openai_base_url,
                api_key=settings.openai_api_key,
                model_name=settings.openai_model,
                timeout_seconds=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
                temperature=settings.llm_temperature,
            )
        else:
            model_gateway = NotImplementedModelGateway(
                settings.llm_provider,
                settings.openai_model or None,
                configured=False,
            )
    else:
        model_gateway = DisabledModelGateway(settings.llm_provider)

    retrieval_gateway: RetrievalGateway
    knowledge_lifecycle: KnowledgeBaseLifecycle
    if settings.rag_enabled:
        if settings.rag_configured:
            runtime_state = KnowledgeBaseRuntimeState(KnowledgeBaseStatus(
                enabled=True,
                configured=True,
                ready=False,
                mode="DEGRADED",
                collection_name=settings.chroma_collection_name,
                last_error="RAG_NOT_INITIALIZED",
            ))
            embedding_client: EmbeddingClient
            embedding_client_class = (
                VolcengineMultimodalEmbeddingClient
                if settings.embedding_provider.strip().casefold() == "volcengine_multimodal"
                else OpenAICompatibleEmbeddingClient
            )
            embedding_client = embedding_client_class(
                base_url=settings.effective_embedding_base_url,
                api_key=settings.effective_embedding_api_key,
                model_name=settings.embedding_model,
                timeout_seconds=settings.llm_timeout_seconds,
                max_retries=settings.llm_max_retries,
                batch_size=settings.embedding_batch_size,
            )
            vector_store = ChromaVectorStore(
                settings.chroma_persist_dir,
                settings.chroma_collection_name,
            )
            retrieval_gateway = ChromaRetrievalGateway(
                embedding_client,
                vector_store,
                runtime_state,
                top_k=settings.rag_top_k,
                score_threshold=settings.rag_score_threshold,
            )
            knowledge_lifecycle = ChromaKnowledgeBaseLifecycle(
                policy_data_dir=settings.policy_data_dir,
                loader=LocalKnowledgeLoader(),
                splitter=StructuredKnowledgeSplitter(
                    settings.rag_chunk_size,
                    settings.rag_chunk_overlap,
                ),
                embedding_client=embedding_client,
                vector_store=vector_store,
                runtime_state=runtime_state,
            )
        else:
            retrieval_gateway = NotImplementedRetrievalGateway(
                settings.chroma_collection_name,
                configured=False,
            )
            knowledge_lifecycle = NotImplementedKnowledgeBaseLifecycle(
                settings.chroma_collection_name,
                configured=False,
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
    agent_store = PostgreSQLAgentRunStore(SessionLocal)
    return ApplicationContainer(
        settings=settings,
        model_gateway=model_gateway,
        retrieval_gateway=retrieval_gateway,
        knowledge_lifecycle=knowledge_lifecycle,
        recruitment_knowledge_service=knowledge_service,
        recruitment_runner_dependencies=dependencies,
        agent_run_store=agent_store,
    )


@lru_cache(maxsize=1)
def get_application_container() -> ApplicationContainer:
    return _build_application_container(get_settings())


def reset_application_container() -> None:
    get_application_container.cache_clear()
