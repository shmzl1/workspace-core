"""Payroll Tool metadata only; no confirmation or mutation is implemented."""

from typing import Mapping, Protocol

from app.agents.shared import ToolContract


class PayrollServiceTool(Protocol):
    def invoke(self, payload: Mapping[str, object]) -> Mapping[str, object]: ...


PAYROLL_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="read_payroll_pre_review",
        description="经薪资 Service、权限校验和审计读取预审结果。",
        service_boundary="PayrollPreAuditService",
        permission="payroll.review.read",
        read_only=True,
        sensitive=True,
        input_fields=("actor_user_id", "review_record_ids"),
        output_fields=("review_summaries", "line_items"),
    ),
)
