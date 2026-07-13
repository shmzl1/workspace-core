"""Contract checks for the LLM/RAG integration prerequisites."""

import asyncio
import inspect
from datetime import date
from pathlib import Path

import pytest
from pydantic import ValidationError

from app.agents.runtime.dependencies import RecruitmentRunnerDependencies
from app.agents.shared import (
    DisabledModelGateway,
    ModelGatewayDisabledError,
    ModelGatewayInput,
    NotImplementedModelGateway,
)
from app.core.config import Settings
from app.core.container import _build_application_container
from app.modules.recruitment.services import RecruitmentKnowledgeAdapter, RecruitmentKnowledgeService
from app.rag import (
    DisabledRetrievalGateway,
    KnowledgeBaseDisabledError,
    KnowledgeMappingError,
    NotImplementedRetrievalGateway,
)
from app.rag.schemas import (
    KnowledgeChunk,
    PolicyDocumentMetadata,
    RetrievalHit,
    RetrievalQuery,
    RetrievalResult,
)
from app.agents.workflows.recruitment_decision.contracts import (
    RecruitmentGoal,
    RecruitmentJobContext,
    RecruitmentRunContext,
    RecruitmentRunRequest,
)


def build_context() -> RecruitmentRunContext:
    return RecruitmentRunContext(
        request=RecruitmentRunRequest(goal=RecruitmentGoal(job_id=1, target_headcount=1)),
        job=RecruitmentJobContext(
            job_id=1, job_code="JOB-001", job_title="后端工程师", department="技术部",
            status="OPEN", source_version="job-v1", effective_date=date(2026, 7, 10),
        ),
    )


def test_model_gateways_are_async_and_never_fabricate_output() -> None:
    assert inspect.iscoroutinefunction(DisabledModelGateway.generate)
    request = ModelGatewayInput(task_name="status", output_schema_name="Status")

    async def scenario() -> None:
        disabled = DisabledModelGateway()
        assert (await disabled.get_status()).mode == "DISABLED"
        with pytest.raises(ModelGatewayDisabledError):
            await disabled.generate(request)
        pending = NotImplementedModelGateway("openai_compatible", "model", configured=True)
        assert (await pending.get_status()).mode == "NOT_IMPLEMENTED"
        with pytest.raises(RuntimeError):
            await pending.generate(request)

    asyncio.run(scenario())


def test_optional_integrations_can_be_disabled_without_credentials() -> None:
    settings = Settings(_env_file=None, database_url="sqlite+pysqlite:///:memory:", llm_enabled=False, rag_enabled=False)
    assert settings.llm_configured is False
    assert settings.rag_configured is False
    container = _build_application_container(settings)
    assert isinstance(container.recruitment_runner_dependencies, RecruitmentRunnerDependencies)
    assert not hasattr(container, "session")


def test_invalid_chunk_overlap_is_rejected() -> None:
    with pytest.raises(ValidationError):
        Settings(_env_file=None, database_url="sqlite+pysqlite:///:memory:", rag_chunk_size=100, rag_chunk_overlap=100)


def test_retrieval_gateways_never_return_fake_results() -> None:
    async def scenario() -> None:
        query = RetrievalQuery(text="岗位标准")
        disabled = DisabledRetrievalGateway()
        with pytest.raises(KnowledgeBaseDisabledError):
            await disabled.retrieve(query)
        pending = NotImplementedRetrievalGateway("policies")
        assert (await pending.get_status()).mode == "NOT_IMPLEMENTED"
        with pytest.raises(RuntimeError):
            await pending.retrieve(query)

    asyncio.run(scenario())


def test_adapter_preserves_source_fields_and_rejects_incomplete_structure() -> None:
    source = PolicyDocumentMetadata(
        source_id="policy-1", title="岗位标准", document_type="JOB_STANDARD",
        department="技术部", job_code="JOB-001", version="v1",
        effective_from=date(2026, 1, 1), effective_to=date(2026, 12, 31),
    )
    query = RetrievalQuery(text="岗位标准")
    result = RetrievalResult(
        query=query,
        hits=[RetrievalHit(
            chunk=KnowledgeChunk(
                chunk_id="chunk-1", source=source, text="真实有限摘录", ordinal=0,
                attributes={"required_skills": ["Python"], "preferred_skills": [], "min_experience_months": 24},
            ),
            relevance=0.9,
            retrieval_method="HYBRID",
        )],
        mode="HYBRID",
    )
    summary, _ = RecruitmentKnowledgeAdapter().to_domain(build_context(), result)
    mapped = summary.sources[0]
    assert mapped.source_id == "policy-1"
    assert mapped.effective_to == date(2026, 12, 31)
    assert mapped.excerpt == "真实有限摘录"
    with pytest.raises(KnowledgeMappingError):
        RecruitmentKnowledgeAdapter().to_domain(build_context(), result.model_copy(update={"hits": []}))


def test_mapping_failure_uses_truthful_local_fallback() -> None:
    class EmptyGateway:
        async def retrieve(self, query: RetrievalQuery) -> RetrievalResult:
            return RetrievalResult(query=query, mode="HYBRID")

        async def get_status(self):  # pragma: no cover - protocol completeness
            return None

        async def aclose(self) -> None:
            return None

    summary, _ = asyncio.run(RecruitmentKnowledgeService(retrieval_gateway=EmptyGateway()).retrieve(build_context()))  # type: ignore[arg-type]
    assert summary.retrieval_mode == "LOCAL_HYBRID_FALLBACK"
    assert summary.warnings == ["RAG_MAPPING_FAILED_LOCAL_FALLBACK"]


def test_building_container_does_not_create_runtime_directories(tmp_path: Path) -> None:
    chroma_path = tmp_path / "chroma"
    policy_path = tmp_path / "policies"
    settings = Settings(
        _env_file=None,
        database_url="sqlite+pysqlite:///:memory:",
        chroma_persist_dir=str(chroma_path),
        policy_data_dir=str(policy_path),
    )
    _build_application_container(settings)
    assert not chroma_path.exists()
    assert not policy_path.exists()


def test_enabled_integrations_start_degraded_until_runtime_validation() -> None:
    async def scenario() -> None:
        settings = Settings(
            _env_file=None,
            database_url="sqlite+pysqlite:///:memory:",
            llm_enabled=True,
            openai_base_url="https://model.invalid/v1",
            openai_api_key="secret-value",
            openai_model="example-model",
            rag_enabled=True,
            embedding_model="example-embedding",
        )
        container = _build_application_container(settings)
        status = await container.get_integration_status()
        assert status.llm.mode == "DEGRADED"
        assert status.rag.mode == "DEGRADED"
        assert status.overall_mode == "DEGRADED"
        assert "secret-value" not in status.model_dump_json()

    asyncio.run(scenario())


def test_runner_and_api_use_injected_dependencies() -> None:
    from app.agents.runtime import recruitment_runner
    from app.api.v1.endpoints import agent

    runner_source = inspect.getsource(recruitment_runner.run_recruitment_strategy)
    api_source = inspect.getsource(agent.create_recruitment_run)
    assert "EnterpriseKnowledgeTool()" not in runner_source
    assert "CandidateProfileTool()" not in runner_source
    assert "dependencies.knowledge_tool.invoke" in runner_source
    assert "container.recruitment_runner_dependencies" in api_source
    assert "sqlalchemy" not in inspect.getsource(recruitment_runner).casefold()
    assert "Session" not in inspect.signature(recruitment_runner.run_recruitment_strategy).parameters


def test_health_status_does_not_expose_credentials(monkeypatch: pytest.MonkeyPatch) -> None:
    from app import main as main_module

    settings = Settings(
        _env_file=None,
        database_url="postgresql+psycopg://user:database-secret@localhost:5433/talentflow",
        llm_enabled=True,
        openai_base_url="https://model.invalid/v1",
        openai_api_key="api-secret",
        openai_model="example-model",
    )
    container = _build_application_container(settings)
    monkeypatch.setattr(main_module, "get_application_container", lambda: container)
    response = asyncio.run(main_module.health())
    serialized = response.model_dump_json()

    assert "api-secret" not in serialized
    assert "database-secret" not in serialized
    assert "DEGRADED" in serialized
    assert "POSTGRESQL" in serialized
