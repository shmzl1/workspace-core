"""Knowledge Tool metadata only; no retrieval is performed."""

from typing import Mapping, Protocol

from app.agents.shared import ToolContract


class KnowledgeServiceTool(Protocol):
    def invoke(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


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
