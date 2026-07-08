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
    """Placeholder for server-side salary permission orchestration."""

    pass
