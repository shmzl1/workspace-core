"""AI Agent Tools for employee service (attendance, leave, and salary)."""

from typing import Any
from sqlalchemy.orm import Session
from app.modules.attendance.service import AttendanceService
from app.modules.employee.service import EmployeeService
from app.modules.payroll.services.employee_salary_service import EmployeeSalaryService


def get_my_monthly_attendance_summary(
    year: int,
    month: int,
    db: Session,
    current_employee_id: int,
) -> dict[str, Any]:
    """获取当前登录员工本人的月度考勤统计汇总数据。

    Args:
        year: 汇总年份（例如 2026）
        month: 汇总月份（1 到 12 之间的整数）
        db: 数据库 Session 连接，由运行时注入
        current_employee_id: 当前登录员工的ID，由运行时注入

    Returns:
        包含当月迟到、早退、缺勤次数以及当年度年假额度详情的考勤月度统计汇总字典。
    """
    service = AttendanceService(db)
    return service.get_monthly_summary(current_employee_id, year, month)


def get_my_annual_leave_balance(
    year: int,
    db: Session,
    current_employee_id: int,
) -> dict[str, Any]:
    """查询当前登录员工本人在指定年份的可用年假及调休余额。

    Args:
        year: 查询年份（例如 2026）
        db: 数据库 Session 连接，由运行时注入
        current_employee_id: 当前登录员工的ID，由运行时注入

    Returns:
        包含总年假天数、已用年假天数等信息的年假额度字典。
    """
    service = EmployeeService(db)
    return service.get_annual_leave(current_employee_id, year)


def get_my_salary_details(
    db: Session,
    current_employee_id: int,
    actor_user_id: int,
    actor_role: str,
    actor_permissions: list[str],
) -> dict[str, Any]:
    """查询当前登录员工本人的薪资详细信息，支持权限自动脱敏与读取操作审计。

    Args:
        db: 数据库 Session 连接，由运行时注入
        current_employee_id: 当前登录员工的ID（目标查询员工），由运行时注入
        actor_user_id: 当前发起请求的用户ID，由运行时注入
        actor_role: 当前发起请求的用户角色，由运行时注入
        actor_permissions: 当前发起请求的用户权限编码列表，由运行时注入

    Returns:
        脱敏且包含安全字段的员工薪资详情字典。
    """
    service = EmployeeSalaryService(db)
    return service.get_employee_salary(
        actor_user_id=actor_user_id,
        actor_role=actor_role,
        actor_permissions=actor_permissions,
        actor_employee_id=current_employee_id,
        target_employee_id=current_employee_id,
    )
