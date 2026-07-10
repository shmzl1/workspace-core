"""Compatibility employee tools backed only by business Services.

New Agent runtime code should inject Service-oriented tools instead of passing a
database Session into the runner.  These functions remain available for the
existing public import path while delegating all business work to Services.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from sqlalchemy.orm import Session

from app.agents.shared import ToolContract
EMPLOYEE_TOOL_CONTRACTS: tuple[ToolContract, ...] = (
    ToolContract(
        name="get_self_attendance",
        description="读取当前员工本人今日或月度考勤。",
        service_boundary="AttendanceService",
        permission="attendance.self.read",
        read_only=True,
        sensitive=False,
        input_fields=("actor_user_id", "employee_id", "period"),
        output_fields=("attendance_summary",),
    ),
    ToolContract(
        name="get_self_salary_summary",
        description="经权限校验读取当前员工本人薪资摘要。",
        service_boundary="EmployeeSalaryService",
        permission="payroll.self.read",
        read_only=True,
        sensitive=True,
        input_fields=("actor_user_id", "employee_id"),
        output_fields=("salary_summary",),
    ),
)


def get_my_monthly_attendance_summary(
    year: int,
    month: int,
    db: Session,
    current_employee_id: int,
) -> dict[str, Any]:
    """Return the current employee's monthly attendance through its Service."""

    from app.modules.attendance.service import AttendanceService

    return AttendanceService(db).get_monthly_summary(current_employee_id, year, month)


def get_my_annual_leave_balance(
    year: int,
    db: Session,
    current_employee_id: int,
) -> dict[str, Any]:
    """Return the current employee's leave balance through its Service."""

    from app.modules.employee.service import EmployeeService

    return EmployeeService(db).get_annual_leave(current_employee_id, year)


def get_my_salary_details(
    db: Session,
    current_employee_id: int,
    actor_user_id: int,
    actor_role: str,
    actor_permissions: list[str],
) -> dict[str, Any]:
    """Return authorized self salary data through the salary Service."""

    from app.modules.payroll.services.employee_salary_service import EmployeeSalaryService

    return EmployeeSalaryService(db).get_employee_salary(
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        actor_permissions=actor_permissions,
        actor_employee_id=current_employee_id,
        target_employee_id=current_employee_id,
    )


__all__ = [
    "EMPLOYEE_TOOL_CONTRACTS",
    "get_my_annual_leave_balance",
    "get_my_monthly_attendance_summary",
    "get_my_salary_details",
]
