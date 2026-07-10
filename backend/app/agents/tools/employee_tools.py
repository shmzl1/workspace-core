"""Canonical employee Tool exports with the legacy path kept compatible."""

from app.agents.tools.employee_service import (
    EMPLOYEE_TOOL_CONTRACTS,
    get_my_annual_leave_balance,
    get_my_monthly_attendance_summary,
    get_my_salary_details,
)

__all__ = [
    "EMPLOYEE_TOOL_CONTRACTS",
    "get_my_annual_leave_balance",
    "get_my_monthly_attendance_summary",
    "get_my_salary_details",
]
