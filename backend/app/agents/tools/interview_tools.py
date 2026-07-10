"""Interview Tool metadata only; no scheduling or evaluation execution."""

from typing import Mapping, Protocol

from app.agents.shared import ToolContract


class InterviewServiceTool(Protocol):
    def invoke(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


INTERVIEW_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="read_interview_evaluation_input",
        description="读取已有结构化面试数据；无数据时返回待面试状态。",
        service_boundary="InterviewService",
        permission="interview.read",
        read_only=True,
        sensitive=True,
        input_fields=("candidate_id", "interview_id"),
        output_fields=("interview_evaluation_input",),
    ),
)
