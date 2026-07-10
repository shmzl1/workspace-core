"""Stable permission codes and role defaults used for account initialization."""

EMPLOYEE_PERMISSIONS = (
    "employee.self.read", "attendance.self.read", "attendance.self.manage",
    "leave.self.read", "payroll.self.read", "policy.read", "agent.employee.use",
)
MANAGER_PERMISSIONS = (
    "employee.self.read", "employee.department.read", "attendance.self.read",
    "attendance.self.manage", "leave.self.read", "payroll.self.read",
    "payroll.department.read", "interview.read", "policy.read", "agent.employee.use",
)
HR_PERMISSIONS = (
    "employee.self.read", "recruitment.read", "recruitment.manage", "candidate.read",
    "candidate.score", "candidate.stage.manage", "interview.read", "interview.manage",
    "reporting.recruitment.read", "payroll.masked.read", "policy.read", "audit.read",
    "agent.hr.use",
)
PAYROLL_ADMIN_PERMISSIONS = (
    "employee.self.read", "payroll.self.read", "payroll.all.read", "payroll.review.read",
    "payroll.review.manage", "audit.read", "policy.read",
)

ROLE_DEFAULT_PERMISSIONS: dict[str, list[str]] = {
    "EMPLOYEE": list(EMPLOYEE_PERMISSIONS),
    "DEPARTMENT_MANAGER": list(MANAGER_PERMISSIONS),
    "HR_SPECIALIST": list(HR_PERMISSIONS),
    "PAYROLL_ADMIN": list(PAYROLL_ADMIN_PERMISSIONS),
}


def normalize_permissions(value: object) -> list[str]:
    if not isinstance(value, (list, tuple, set)):
        return []
    return sorted({str(item).strip() for item in value if isinstance(item, str) and item.strip()})
