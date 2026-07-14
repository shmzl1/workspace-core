"""Non-human-only contract tests for persisted Agent, LLM and RAG integration."""

import asyncio
from datetime import date

from pydantic import SecretStr

from app.agents.shared import ModelGatewayInput, ModelGatewayOutput, OpenAICompatibleModelGateway
from app.agents.workflows.recruitment_decision.contracts import (
    DecisionReviewSummary,
    HRReportSummary,
    RecruitmentExecutionPlan,
    RecruitmentGoal,
    RecruitmentJobContext,
)
from app.agents.workflows.recruitment_decision.report_agent import enhance_hr_report
from app.agents.workflows.recruitment_decision.strategy_agent import enhance_recruitment_execution_plan
from app.modules.agent_runtime.models import AgentEventRecord, AgentRun, AgentRunNode, AgentToolCall
from app.rag.ingestion.contracts import LoadedKnowledgeDocument
from app.rag.ingestion.splitter import StructuredKnowledgeSplitter
from app.rag.schemas import PolicyDocumentMetadata


class StaticModelGateway:
    def __init__(self, output: dict) -> None:
        self.output = output
        self.requests: list[ModelGatewayInput] = []

    async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
        self.requests.append(request)
        return ModelGatewayOutput(
            structured_output=self.output,
            provider="test",
            model_name="test-model",
            duration_ms=12,
        )

    async def get_status(self):
        return None

    async def aclose(self) -> None:
        return None


def test_agent_runtime_models_use_expected_tables() -> None:
    assert AgentRun.__tablename__ == "agent_runs"
    assert AgentRunNode.__tablename__ == "agent_run_nodes"
    assert AgentEventRecord.__tablename__ == "agent_events"
    assert AgentToolCall.__tablename__ == "agent_tool_calls"
    assert AgentRun.__table__.c.state_json.type.__class__.__name__ == "JSONB"
    assert AgentRun.__table__.c.snapshot_json.type.__class__.__name__ == "JSONB"
    assert next(iter(AgentRun.__table__.c.owner_user_id.foreign_keys)).ondelete == "SET NULL"


def test_strategy_model_enhancement_cannot_change_deterministic_plan() -> None:
    goal = RecruitmentGoal(job_id=1, target_headcount=1)
    plan = RecruitmentExecutionPlan(
        goal=goal,
        candidate_ids=[10, 11],
        candidate_count=2,
        required_nodes=["recruitment_strategy", "job_match"],
        executed_nodes=["recruitment_strategy", "job_match"],
        skipped_nodes=["interview_evaluation"],
    )
    job = RecruitmentJobContext(
        job_id=1,
        job_code="JOB-JAVA-INTERN-001",
        job_title="Java 后端开发实习生",
        department="研发部",
        status="OPEN",
        source_version="v1",
        effective_date=date(2026, 1, 1),
    )
    gateway = StaticModelGateway({
        "strategy_summary": "建议优先核查项目证据。",
        "next_actions": ["建议安排人工复核"],
        "risk_reminders": ["建议关注证据完整性"],
    })
    enhanced = asyncio.run(enhance_recruitment_execution_plan(
        plan,
        job,
        gateway,
    ))
    assert enhanced.candidate_ids == [10, 11]
    assert enhanced.required_nodes == plan.required_nodes
    assert enhanced.skipped_nodes == ["interview_evaluation"]
    assert enhanced.generation_mode == "LLM_ENHANCED"
    assert enhanced.model_name == "test-model"
    assert gateway.requests[0].thinking_type == "disabled"
    assert gateway.requests[0].max_completion_tokens == 512


def test_report_model_enhancement_preserves_rankings_reviews_and_sources() -> None:
    report = HRReportSummary(
        goal=RecruitmentGoal(job_id=1, target_headcount=1),
        candidate_rankings=[10, 11],
        candidate_reviews=[DecisionReviewSummary(candidate_id=10)],
        requires_human_decision=True,
    )
    gateway = StaticModelGateway({
        "executive_summary": "建议由 HR 结合证据完成人工决定。",
        "talent_gaps": ["项目证据仍需补充"],
        "next_actions": ["建议复核结构化面试资料"],
    })
    enhanced = asyncio.run(enhance_hr_report(
        report,
        gateway,
    ))
    assert enhanced.candidate_rankings == [10, 11]
    assert enhanced.candidate_reviews == report.candidate_reviews
    assert enhanced.knowledge_sources == report.knowledge_sources
    assert enhanced.requires_human_decision is True
    assert enhanced.generation_mode == "LLM_ENHANCED"
    assert gateway.requests[0].thinking_type == "disabled"
    assert gateway.requests[0].max_completion_tokens == 768


def test_slow_model_enhancements_fall_back_within_node_budget() -> None:
    class SlowModelGateway(StaticModelGateway):
        async def generate(self, request: ModelGatewayInput) -> ModelGatewayOutput:
            await asyncio.sleep(0.05)
            return await super().generate(request)

    goal = RecruitmentGoal(job_id=1, target_headcount=1)
    plan = RecruitmentExecutionPlan(goal=goal, candidate_count=0)
    job = RecruitmentJobContext(
        job_id=1,
        job_code="JOB-JAVA-INTERN-001",
        job_title="Java 后端开发实习生",
        department="研发部",
        status="OPEN",
        source_version="v1",
        effective_date=date(2026, 1, 1),
    )
    report = HRReportSummary(goal=goal)

    async def scenario() -> tuple[RecruitmentExecutionPlan, HRReportSummary]:
        strategy = await enhance_recruitment_execution_plan(
            plan,
            job,
            SlowModelGateway({}),
            timeout_seconds=0.001,
        )
        hr_report = await enhance_hr_report(
            report,
            SlowModelGateway({}),
            timeout_seconds=0.001,
        )
        return strategy, hr_report

    strategy, hr_report = asyncio.run(scenario())
    assert strategy.generation_mode == "RULE_BASED_FALLBACK"
    assert strategy.fallback_used is True
    assert hr_report.generation_mode == "RULE_BASED_FALLBACK"
    assert hr_report.fallback_used is True


def test_openai_compatible_gateway_normalizes_endpoint_and_parses_json_fence() -> None:
    class Response:
        status_code = 200

        @staticmethod
        def json():
            return {
                "choices": [{"message": {"content": "```json\n{\"summary\":\"ok\"}\n```"}}],
                "usage": {"prompt_tokens": 1, "completion_tokens": 2, "total_tokens": 3},
            }

    class Client:
        async def post(self, *args, **kwargs):
            return Response()

        async def aclose(self) -> None:
            return None

    gateway = OpenAICompatibleModelGateway(
        base_url="https://model.invalid/v1/",
        api_key=SecretStr("secret"),
        model_name="example-model",
    )
    gateway._client = Client()  # type: ignore[assignment]
    output = asyncio.run(gateway.generate(ModelGatewayInput(
        task_name="test",
        system_context={"prompt": "JSON only"},
        structured_input={"value": 1},
        output_schema_name="TestOutput",
    )))
    assert gateway._endpoint == "https://model.invalid/v1/chat/completions"
    assert output.structured_output == {"summary": "ok"}
    assert output.total_tokens == 3


def test_structured_splitter_is_stable_and_preserves_metadata() -> None:
    document = LoadedKnowledgeDocument(
        metadata=PolicyDocumentMetadata(
            source_id="source-1",
            title="岗位标准",
            document_type="JOB_STANDARD",
        ),
        content="# 标题\n\n第一段内容。\n\n第二段内容。" * 8,
        attributes={"required_skills": ["Java"]},
    )
    splitter = StructuredKnowledgeSplitter(chunk_size=80, chunk_overlap=10)
    first = list(splitter.split(document))
    second = list(splitter.split(document))
    assert [chunk.chunk_id for chunk in first] == [chunk.chunk_id for chunk in second]
    assert all(chunk.source.source_id == "source-1" for chunk in first)
    assert all(chunk.attributes["required_skills"] == ["Java"] for chunk in first)
