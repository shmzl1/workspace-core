"""Payroll access service — salary permission check + audit logging."""

from dataclasses import dataclass
from importlib import import_module
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.employee.models import Employee
from app.modules.audit.service import AuditLogService
from app.shared.human_only_bridge import HumanOnlyContract, load_human_only_function


# ── Human-Only Contract 元数据（供 bridge / 调试台使用）──────────────────────
SALARY_ACCESS_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.salary_access_control",
    file_path="backend/app/human_only/salary_access_control.py",
    function_name="check_salary_access",
    not_ready_message="薪资权限校验服务暂未完成配置",
)


# ── 本地 fallback 实现（salary_access_control.py 缺失时自动启用）─────────────
def check_salary_access_local(
    actor_role: str,
    actor_employee_id: int | None,
    target_employee_id: int,
    target_department: str = "",
    relation: str | None = None,
    **kwargs,
) -> dict:
    # 1. 员工查询本人
    if actor_employee_id == target_employee_id:
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许员工查询本人薪资信息",
        }

    # 2. 薪酬管理员
    if actor_role == "PAYROLL_ADMIN":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许薪酬管理员查询所有薪资信息",
        }

    # 3. HR 专员
    if actor_role == "HR_SPECIALIST":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from"],
            "fields": ["base_salary", "currency", "effective_from"],
            "reason": "允许HR专员查询薪资信息（已脱敏截止日期）",
        }

    # 4. 部门经理查本部门员工
    if actor_role == "DEPARTMENT_MANAGER" and relation == "manager":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency"],
            "fields": ["base_salary", "currency"],
            "reason": "允许部门经理查询本部门员工薪资信息（仅基本工资与币种）",
        }

    return {
        "allowed": False,
        "accessible_fields": [],
        "fields": [],
        "reason": "无权访问此员工的薪资数据",
    }


# ── 优先尝试加载 human_only 实现，缺失则回退到本地 fallback ──────────────────
def _resolve_check_fn():
    fn = load_human_only_function(SALARY_ACCESS_CONTRACT)
    return fn if fn is not None else check_salary_access_local


@dataclass(frozen=True)
class SalaryAccessDecision:
    allowed: bool
    fields: list[str]
    reason: str


class PayrollAccessService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_service = AuditLogService(db)

    @staticmethod
    def _read_result(result: Any, key: str, default: Any) -> Any:
        if isinstance(result, dict):
            return result.get(key, default)
        return getattr(result, key, default)

    def check_salary_access(
        self,
        identity: DemoIdentity,
        target_employee_id: int,
        requested_fields: list[str],
    ) -> SalaryAccessDecision:
        check_fn = _resolve_check_fn()
        result = check_fn(
            actor_user_id=identity.user_id,
            actor_role=identity.role,
            actor_employee_id=identity.employee_id,
            target_employee_id=target_employee_id,
            requested_fields=requested_fields,
            relation="self" if identity.employee_id == target_employee_id else "none",
        )
        return SalaryAccessDecision(
            allowed=bool(self._read_result(result, "allowed", False)),
            fields=list(
                self._read_result(
                    result, "fields", self._read_result(result, "accessible_fields", [])
                )
            ),
            reason=str(self._read_result(result, "reason", "")),
        )

    def verify_and_log_access(
        self,
        actor_user_id: int,
        actor_role: str,
        actor_employee_id: int | None,
        target_employee_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None,
    ) -> list[str]:
        """
        校验调用方是否有权查询目标员工薪资。
        自动处理关系判定、调用权限算法、写入审计日志，并在无权时抛出异常。
        """
        # 获取目标员工信息
        target_emp = self.db.query(Employee).filter(Employee.id == target_employee_id).first()
        if not target_emp:
            raise TalentFlowError("EMPLOYEE_NOT_FOUND", "目标员工不存在")

        # 获取请求方员工信息
        actor_emp = None
        if actor_employee_id:
            actor_emp = self.db.query(Employee).filter(Employee.id == actor_employee_id).first()

        # 判断关系
        relation = "none"
        if actor_employee_id == target_employee_id:
            relation = "self"
        elif target_emp.manager_employee_id == actor_employee_id:
            relation = "manager"
        elif (
            actor_role == "DEPARTMENT_MANAGER"
            and actor_emp
            and target_emp.department == actor_emp.department
        ):
            relation = "manager"

        # 调用权限校验
        check_fn = _resolve_check_fn()
        result = check_fn(
            actor_role=actor_role,
            actor_employee_id=actor_employee_id,
            target_employee_id=target_employee_id,
            target_department=target_emp.department,
            relation=relation,
        )

        allowed = result.get("allowed", False)
        accessible_fields = result.get("accessible_fields", [])
        reason = result.get("reason", "无权限")

        # 写入审计日志
        self.audit_service.log_action(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            target_employee_id=target_employee_id,
            action="QUERY_SALARY",
            resource_type="SALARY",
            requested_fields=["base_salary", "currency", "effective_from", "effective_to"],
            result="ALLOWED" if allowed else "DENIED",
            reason=reason,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        if not allowed:
            raise TalentFlowError("PERMISSION_DENIED", reason)

        return accessible_fields
