"""Payroll access service boundary.

This service is the only future entry point allowed to call
human_only.salary_access_control.
"""

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from app.core.security import DemoIdentity


@dataclass(frozen=True)
class SalaryAccessDecision:
    allowed: bool
    fields: list[str]
    reason: str


class PayrollAccessService:
    """Server-side salary permission orchestration."""

    @staticmethod
    def _read_result(result: Any, key: str, default: Any) -> Any:
        if isinstance(result, dict):
            return result.get(key, default)
        return getattr(result, key, default)

    def check_salary_access(self, identity: DemoIdentity, target_employee_id: int, requested_fields: list[str]) -> SalaryAccessDecision:
        try:
            module = import_module("app.human_only.salary_access_control")
            check_salary_access = getattr(module, "check_salary_access")
        except (ModuleNotFoundError, AttributeError):
            return SalaryAccessDecision(
                allowed=False,
                fields=[],
                reason="薪资权限禁飞区函数尚未由人工负责人提供，系统拒绝访问",
            )

        result = check_salary_access(
            actor_user_id=identity.user_id,
            actor_role=identity.role,
            actor_employee_id=identity.employee_id,
            target_employee_id=target_employee_id,
            requested_fields=requested_fields,
        )
        return SalaryAccessDecision(
            allowed=bool(self._read_result(result, "allowed", False)),
            fields=list(self._read_result(result, "fields", [])),
            reason=str(self._read_result(result, "reason", "")),
        )
