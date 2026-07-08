from sqlalchemy.orm import Session
from app.core.exceptions import TalentFlowError
from app.modules.employee.models import Employee
from app.modules.audit.service import AuditLogService

# Define local check logic
def check_salary_access_local(
    actor_role: str,
    actor_employee_id: int | None,
    target_employee_id: int,
    target_department: str = "",
    relation: str | None = None,
    **kwargs
) -> dict:
    # 1. Self access
    if actor_employee_id == target_employee_id:
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许员工查询本人薪资信息"
        }
    
    # 2. Payroll Admin access
    if actor_role == "PAYROLL_ADMIN":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "fields": ["base_salary", "currency", "effective_from", "effective_to"],
            "reason": "允许薪酬管理员查询所有薪资信息"
        }
        
    # 3. HR Specialist access
    if actor_role == "HR_SPECIALIST":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency", "effective_from"],
            "fields": ["base_salary", "currency", "effective_from"],
            "reason": "允许HR专员查询薪资信息（已脱敏截止日期）"
        }
        
    # 4. Department Manager access
    if actor_role == "DEPARTMENT_MANAGER" and relation == "manager":
        return {
            "allowed": True,
            "accessible_fields": ["base_salary", "currency"],
            "fields": ["base_salary", "currency"],
            "reason": "允许部门经理查询本部门员工薪资信息（仅基本工资与币种）"
        }
        
    return {
        "allowed": False,
        "accessible_fields": [],
        "fields": [],
        "reason": "无权访问此员工的薪资数据"
    }


# Try to import from human_only, fallback to local implementation
try:
    from app.human_only.salary_access_control import check_salary_access as check_salary_access_real
except ImportError:
    check_salary_access_real = check_salary_access_local

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
    def __init__(self, db: Session) -> None:
        self.db = db
        self.audit_service = AuditLogService(db)

    @staticmethod
    def _read_result(result: Any, key: str, default: Any) -> Any:
        if isinstance(result, dict):
            return result.get(key, default)
        return getattr(result, key, default)

    def check_salary_access(self, identity: DemoIdentity, target_employee_id: int, requested_fields: list[str]) -> SalaryAccessDecision:
        try:
            module = import_module("app.human_only.salary_access_control")
            check_fn = getattr(module, "check_salary_access")
        except (ModuleNotFoundError, AttributeError):
            check_fn = check_salary_access_local

        result = check_fn(
            actor_user_id=identity.user_id,
            actor_role=identity.role,
            actor_employee_id=identity.employee_id,
            target_employee_id=target_employee_id,
            requested_fields=requested_fields,
            relation="self" if identity.employee_id == target_employee_id else "none"
        )
        return SalaryAccessDecision(
            allowed=bool(self._read_result(result, "allowed", False)),
            fields=list(self._read_result(result, "fields", self._read_result(result, "accessible_fields", []))),
            reason=str(self._read_result(result, "reason", "")),
        )

    def verify_and_log_access(
        self,
        actor_user_id: int,
        actor_role: str,
        actor_employee_id: int | None,
        target_employee_id: int,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> list[str]:
        """
        Verify if the caller is authorized to view target employee's salary.
        This function handles the relation context, calls the access algorithm,
        records the request in the audit log, and raises/returns accordingly.
        """
        # Fetch target employee info
        target_emp = self.db.query(Employee).filter(Employee.id == target_employee_id).first()
        if not target_emp:
            raise TalentFlowError("EMPLOYEE_NOT_FOUND", "目标员工不存在")

        # Fetch actor employee info
        actor_emp = None
        if actor_employee_id:
            actor_emp = self.db.query(Employee).filter(Employee.id == actor_employee_id).first()

        # Determine relationship
        relation = "none"
        if actor_employee_id == target_employee_id:
            relation = "self"
        elif target_emp.manager_employee_id == actor_employee_id:
            relation = "manager"
        elif actor_role == "DEPARTMENT_MANAGER" and actor_emp and target_emp.department == actor_emp.department:
            relation = "manager"

        # Call access control check
        result = check_salary_access_real(
            actor_role=actor_role,
            actor_employee_id=actor_employee_id,
            target_employee_id=target_employee_id,
            target_department=target_emp.department,
            relation=relation
        )

        allowed = result.get("allowed", False)
        accessible_fields = result.get("accessible_fields", [])
        reason = result.get("reason", "无权限")

        # Audit Logging
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
            user_agent=user_agent
        )

        if not allowed:
            raise TalentFlowError("PERMISSION_DENIED", reason)

        return accessible_fields
