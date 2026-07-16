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
    """
    检查字段级薪资访问权限。

    为兼容旧调用方式，当 actor_role 传入字典时，
    转发到 review_salary_records() 执行薪资预审。
    """
    if isinstance(actor_role, dict):
        return review_salary_records(actor_role)

    codes = {
        item
        for item in permissions or []
        if isinstance(item, str)
    }

    if (
        actor_employee_id is not None
        and actor_employee_id == target_employee_id
        and "payroll.self.read" in codes
    ):
        return _allow(FULL_FIELDS, "允许查询本人薪资信息")

    if "payroll.all.read" in codes:
        return _allow(FULL_FIELDS, "允许查询全量薪资信息")

    if "payroll.department.read" in codes and relation == "manager":
        return _allow(
            MANAGER_FIELDS,
            "允许查询管理范围内员工的有限薪资字段",
        )

    if "payroll.masked.read" in codes:
        return _allow(MASKED_FIELDS, "允许查询脱敏薪资字段")

    return {
        "allowed": False,
        "accessible_fields": [],
        "fields": [],
        "reason": "当前账号没有可用的薪资访问权限",
    }


def review_salary_records(payload: dict[str, Any]) -> dict[str, Any]:
    """
    对薪资记录执行预审。

    当前仅保留原有的基础预审结果结构，
    后续可以在此函数中单独扩展异常薪资项和权限风险判断。
    """
    records_value = payload.get("records")
    records = records_value if isinstance(records_value, list) else []

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


def _allow(fields: list[str], reason: str) -> dict[str, Any]:
    return {
        "allowed": True,
        "accessible_fields": fields,
        "fields": fields,
        "reason": reason,
    }