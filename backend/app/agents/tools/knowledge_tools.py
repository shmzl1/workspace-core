"""Knowledge Tool metadata and the Sprint 2.2 local fallback adapter."""

from __future__ import annotations

from typing import TYPE_CHECKING, Protocol

from app.agents.shared import ToolContract
from app.agents.workflows.recruitment_decision.contracts import (
    EnterpriseKnowledgeSummary,
    JobRubric,
    RecruitmentRunContext,
)

if TYPE_CHECKING:
    from app.modules.recruitment.services.recruitment_knowledge_service import RecruitmentKnowledgeService


class KnowledgeServiceTool(Protocol):
    async def invoke(
        self,
        context: RecruitmentRunContext,
    ) -> tuple[EnterpriseKnowledgeSummary, JobRubric]: ...


class EnterpriseKnowledgeTool:
    """Agent Tool delegating to the unified recruitment knowledge Service."""

    def __init__(self, service: RecruitmentKnowledgeService | None = None) -> None:
        if service is None:
            from app.modules.recruitment.services.recruitment_knowledge_service import (
                RecruitmentKnowledgeService,
            )

            service = RecruitmentKnowledgeService()
        self.service = service

    async def invoke(self, context: RecruitmentRunContext) -> tuple[EnterpriseKnowledgeSummary, JobRubric]:
        return await self.service.retrieve(context)


KNOWLEDGE_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="retrieve_enterprise_knowledge",
        description="按岗位、部门、文档类型和生效时间检索企业知识。",
        service_boundary="RAG retrieval contract",
        permission="policy.read",
        read_only=True,
        sensitive=False,
        input_fields=("query", "filters"),
        output_fields=("retrieval_result", "sources"),
    ),
)
