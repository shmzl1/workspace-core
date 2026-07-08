"""Payroll access service boundary."""

from typing import Any

from app.shared.human_only_bridge import HumanOnlyContract, algorithm_not_ready, load_human_only_function


SALARY_ACCESS_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.salary_access_control",
    file_path="backend/app/human_only/salary_access_control.py",
    function_name="check_salary_access",
    not_ready_message="薪资权限校验服务暂未完成配置",
)
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
    """Only payroll engineering entry point for salary permission algorithms."""

    def check_salary_access(self, payload: dict[str, Any]) -> dict[str, Any]:
        check_salary_access = load_human_only_function(SALARY_ACCESS_CONTRACT)
        if check_salary_access is None:
            return algorithm_not_ready(SALARY_ACCESS_CONTRACT, self._fallback(payload))

        try:
            return check_salary_access(payload)
        except NotImplementedError:
            return algorithm_not_ready(SALARY_ACCESS_CONTRACT, self._fallback(payload))

    @staticmethod
    def _fallback(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "requester_role": payload.get("requester", {}).get("role"),
            "record_count": len(payload.get("records", [])),
        }
