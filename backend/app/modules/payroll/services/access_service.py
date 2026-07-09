"""Payroll access service — salary permission check + audit logging."""
 
from dataclasses import dataclass
from typing import Any

# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.employee.models import Employee
from app.modules.audit.service import AuditLogService
from app.shared.human_only_bridge import HumanOnlyContract, load_human_only_function, algorithm_not_ready


# ── Human-Only Contract 元数据（供 bridge / 调试台使用）──────────────────────
SALARY_ACCESS_CONTRACT = HumanOnlyContract(
    module_name="app.human_only.salary_access_control",
    file_path="backend/app/human_only/salary_access_control.py",
    function_name="check_salary_access",
    not_ready_message="薪资权限校验服务暂未完成配置",
)


def _resolve_check_fn():
    fn = load_human_only_function(SALARY_ACCESS_CONTRACT)
    if fn is None:
        raise TalentFlowError("SALARY_ACCESS_NOT_READY", "薪资权限校验服务暂不可用。", 500)
    return fn


@dataclass(frozen=True)
class SalaryAccessDecision:
    allowed: bool
    fields: list[str]
    reason: str


class PayrollAccessService:
    def __init__(self, db: Session = None) -> None:
        self.db = db
        if db is not None:
            self.audit_service = AuditLogService(db)
        else:
            self.audit_service = None

    @staticmethod
    def _read_result(result: Any, key: str, default: Any) -> Any:
        if isinstance(result, dict):
            return result.get(key, default)
        return getattr(result, key, default)

    def check_salary_access(
        self,
        payload_or_identity: dict[str, Any] | DemoIdentity,
        target_employee_id: int | None = None,
        requested_fields: list[str] | None = None,
    ) -> dict[str, Any] | SalaryAccessDecision:
        if isinstance(payload_or_identity, dict):
            # Dict-based check_salary_access for pre_audit_service and test_human_only_algorithm_not_ready
            check_salary_access = load_human_only_function(SALARY_ACCESS_CONTRACT)
            if check_salary_access is None:
                return algorithm_not_ready(SALARY_ACCESS_CONTRACT, self._fallback(payload_or_identity))
            try:
                return check_salary_access(payload_or_identity)
            except (NotImplementedError, TypeError):
                return algorithm_not_ready(SALARY_ACCESS_CONTRACT, self._fallback(payload_or_identity))

        identity = payload_or_identity
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

    @staticmethod
    def _fallback(payload: dict[str, Any]) -> dict[str, Any]:
        return {
            "requester_role": payload.get("requester", {}).get("role"),
            "record_count": len(payload.get("records", [])),
        }

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
            raise TalentFlowError("PERMISSION_DENIED", reason, 403)

        return accessible_fields
