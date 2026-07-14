"""Concurrent in-memory Backend -> Repository -> RAG -> LLM gateway test."""

import asyncio
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass, field
from threading import Lock
from time import perf_counter

from app.agents.shared.model_gateway import ModelGatewayInput, ModelGatewayOutput
from app.rag.ingestion.contracts import LoadedKnowledgeDocument
from app.rag.ingestion.splitter import StructuredKnowledgeSplitter
from app.rag.schemas import PolicyDocumentMetadata


@dataclass(frozen=True)
class KnowledgeQueryRequest:
    request_id: str
    actor_user_id: int
    source_id: str
    query: str


@dataclass
class RequestMetrics:
    backend_durations: list[float] = field(default_factory=list)
    database_durations: list[float] = field(default_factory=list)
    llm_durations: list[float] = field(default_factory=list)
    _lock: Lock = field(default_factory=Lock)

    def record_backend(self, duration: float) -> None:
        with self._lock:
            self.backend_durations.append(duration)

    def record_database(self, duration: float) -> None:
        with self._lock:
            self.database_durations.append(duration)

    def record_llm(self, duration: float) -> None:
        with self._lock:
            self.llm_durations.append(duration)

    def reset(self) -> None:
        with self._lock:
            self.backend_durations.clear()
            self.database_durations.clear()
            self.llm_durations.clear()


class InMemoryKnowledgeRepository:
    """Thread-safe substitute for a Repository database query."""

    def __init__(self, document: LoadedKnowledgeDocument, metrics: RequestMetrics) -> None:
        self._document = document
        self._metrics = metrics
        self._lock = Lock()
        self.request_count = 0

    def fetch_active_document(self, *, source_id: str, query: str) -> LoadedKnowledgeDocument:
        started_at = perf_counter()
        assert source_id == self._document.metadata.source_id
        assert query == "招聘制度中如何保留人工最终决策？"
        with self._lock:
            self.request_count += 1
        document = self._document.model_copy(deep=True)
        self._metrics.record_database(perf_counter() - started_at)
        return document

    def reset_count(self) -> None:
        with self._lock:
            self.request_count = 0


class DeterministicModelGateway:
    """Thread-safe, no-network implementation of the ModelGateway request contract."""

    def __init__(self, metrics: RequestMetrics) -> None:
        self._metrics = metrics
        self._lock = Lock()
        self.request_count = 0

    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
        started_at = perf_counter()
        assert request.task_name == "policy_retrieval_summary"
        assert request.output_schema_name == "KnowledgeSummary"
        assert request.thinking_type == "disabled"
        assert request.max_completion_tokens == 256
        assert request.system_context["prompt"] == "Return an auditable JSON knowledge summary."
        assert request.structured_input["query"] == "招聘制度中如何保留人工最终决策？"
        assert request.structured_input["source_id"] == "concurrency-policy"
        chunks = request.structured_input["chunks"]
        assert isinstance(chunks, list) and chunks
        with self._lock:
            self.request_count += 1
        self._metrics.record_llm(perf_counter() - started_at)
        return ModelGatewayOutput(
            structured_output={
                "source_id": request.structured_input["source_id"],
                "chunk_ids": [chunk["chunk_id"] for chunk in chunks],
                "answer_mode": "SIMULATED_NO_NETWORK",
            },
            provider="test_gateway",
            model_name="test-llm",
            duration_ms=0,
            fallback_used=True,
        )

    def reset_count(self) -> None:
        with self._lock:
            self.request_count = 0


class KnowledgeBackend:
    """Backend request boundary that composes repository, RAG splitter and LLM gateway."""

    def __init__(
        self,
        repository: InMemoryKnowledgeRepository,
        splitter: StructuredKnowledgeSplitter,
        model_gateway: DeterministicModelGateway,
        metrics: RequestMetrics,
    ) -> None:
        self._repository = repository
        self._splitter = splitter
        self._model_gateway = model_gateway
        self._metrics = metrics

    def retrieve_knowledge(self, request: KnowledgeQueryRequest) -> dict[str, object]:
        started_at = perf_counter()
        document = self._repository.fetch_active_document(
            source_id=request.source_id,
            query=request.query,
        )
        chunks = [chunk.model_dump(mode="json") for chunk in self._splitter.split(document)]
        gateway_request = ModelGatewayInput(
            task_name="policy_retrieval_summary",
            system_context={"prompt": "Return an auditable JSON knowledge summary."},
            structured_input={
                "query": request.query,
                "source_id": document.metadata.source_id,
                "chunks": chunks,
            },
            output_schema_name="KnowledgeSummary",
            thinking_type="disabled",
            max_completion_tokens=256,
        )
        gateway_output = asyncio.run(self._model_gateway.generate(gateway_request))
        self._metrics.record_backend(perf_counter() - started_at)
        return {"chunks": chunks, "llm_response": gateway_output.structured_output}


def _report_metrics(reporter, label: str, count: int, durations: list[float], wall_seconds: float | None = None) -> None:
    total_seconds = sum(durations)
    average_ms = (total_seconds / count * 1000) if count else 0.0
    if wall_seconds is None:
        reporter.write_line(
            f"{label}: requests={count}, aggregate={total_seconds:.4f}s, average={average_ms:.3f}ms"
        )
        return
    throughput = count / wall_seconds if wall_seconds else float("inf")
    reporter.write_line(
        f"{label}: requests={count}, wall_time={wall_seconds:.4f}s, "
        f"average={average_ms:.3f}ms, throughput={throughput:.2f} requests/s"
    )


def test_backend_repository_rag_and_llm_requests_are_deterministic_under_concurrency(pytestconfig) -> None:
    worker_count = 8
    request_count = 64
    query = "招聘制度中如何保留人工最终决策？"
    metrics = RequestMetrics()
    source = LoadedKnowledgeDocument(
        metadata=PolicyDocumentMetadata(
            source_id="concurrency-policy",
            title="招聘制度并发测试",
            document_type="POLICY",
        ),
        content=("# 招聘原则\n\n必须保留人工最终决策。\n\n" * 20),
    )
    repository = InMemoryKnowledgeRepository(source, metrics)
    model_gateway = DeterministicModelGateway(metrics)
    backend = KnowledgeBackend(
        repository,
        StructuredKnowledgeSplitter(chunk_size=64, chunk_overlap=8),
        model_gateway,
        metrics,
    )

    def send_backend_request(index: int) -> dict[str, object]:
        return backend.retrieve_knowledge(
            KnowledgeQueryRequest(
                request_id=f"request-{index}",
                actor_user_id=7,
                source_id="concurrency-policy",
                query=query,
            )
        )

    baseline = send_backend_request(-1)
    metrics.reset()
    repository.reset_count()
    model_gateway.reset_count()
    started_at = perf_counter()
    with ThreadPoolExecutor(max_workers=worker_count) as executor:
        results = list(executor.map(send_backend_request, range(request_count)))
    wall_seconds = perf_counter() - started_at

    assert all(result == baseline for result in results)
    assert len(metrics.backend_durations) == request_count
    assert len(metrics.database_durations) == request_count
    assert len(metrics.llm_durations) == request_count
    assert repository.request_count == request_count
    assert model_gateway.request_count == request_count

    reporter = pytestconfig.pluginmanager.get_plugin("terminalreporter")
    if reporter is not None:
        _report_metrics(reporter, "Backend request results", request_count, metrics.backend_durations, wall_seconds)
        _report_metrics(reporter, "Database request results", request_count, metrics.database_durations)
        _report_metrics(reporter, "LLM request results", request_count, metrics.llm_durations)
