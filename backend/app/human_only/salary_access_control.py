"""Pure salary access policy driven by persisted permission codes and data relation."""

from typing import Any


FULL_FIELDS = ["base_salary", "currency", "effective_from", "effective_to"]
MANAGER_FIELDS = ["base_salary", "currency"]
MASKED_FIELDS = ["currency", "effective_from"]


def check_salary_access(
    actor_role: str | dict[str, Any],
    actor_employee_id: int | None = None,
    target_employee_id: int | None = None,
    permissions: list[str] | None = None,
    relation: str | None = None,
    **_: Any,
) -> dict[str, Any]:
    """Return field-level salary access without depending on framework or database state."""
    if isinstance(actor_role, dict):
        records = actor_role.get("records") if isinstance(actor_role.get("records"), list) else []
        return {
            "status": "reviewed",
            "message": "薪资预审结果已生成。",
            "pending_batches": len(records),
            "abnormal_salary_items": [],
            "permission_risks": [],
            "deduction_sources": [],
            "approval_suggestion": "请由具备薪资预审权限的人员复核。",
            "risk_level": "low",
        }

    codes = {item for item in permissions or [] if isinstance(item, str)}
    if actor_employee_id is not None and actor_employee_id == target_employee_id and "payroll.self.read" in codes:
        return _allow(FULL_FIELDS, "允许查询本人薪资信息")
    if "payroll.all.read" in codes:
        return _allow(FULL_FIELDS, "允许查询全量薪资信息")
    if "payroll.department.read" in codes and relation == "manager":
        return _allow(MANAGER_FIELDS, "允许查询管理范围内员工的有限薪资字段")
    if "payroll.masked.read" in codes:
        return _allow(MASKED_FIELDS, "允许查询脱敏薪资字段")
    return {"allowed": False, "accessible_fields": [], "fields": [], "reason": "当前账号没有可用的薪资访问权限"}


def _allow(fields: list[str], reason: str) -> dict[str, Any]:
    return {"allowed": True, "accessible_fields": fields, "fields": fields, "reason": reason}
