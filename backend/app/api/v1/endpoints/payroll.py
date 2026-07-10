"""Payroll route boundary."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, require_any_permission, require_permission
from app.modules.auth.models import User
from app.modules.auth.permissions import normalize_permissions
from app.modules.employee.models import Employee
from app.modules.payroll.schemas.salary import SalaryRead
from app.modules.payroll.services.employee_salary_service import EmployeeSalaryService
from app.shared.response import ApiResponse, ok

router = APIRouter()
SALARY_READ_PERMISSIONS = ("payroll.self.read", "payroll.department.read", "payroll.masked.read", "payroll.all.read")


def get_salary_service(session: Session = Depends(get_db_session)) -> EmployeeSalaryService:
    return EmployeeSalaryService.from_session(session)


@router.get("/me", response_model=ApiResponse[SalaryRead])
def get_my_salary(
    request: Request,
    current_user: User = Depends(require_permission("payroll.self.read")),
    current_employee: Employee = Depends(get_current_employee),
    service: EmployeeSalaryService = Depends(get_salary_service),
) -> ApiResponse[SalaryRead]:
    salary_data = service.get_employee_salary(
        actor_user_id=current_user.id,
        actor_role=current_user.role,
        actor_permissions=normalize_permissions(current_user.permissions),
        actor_employee_id=current_employee.id,
        target_employee_id=current_employee.id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return ok(SalaryRead.model_validate(salary_data))


@router.get("/employee/{employee_id}", response_model=ApiResponse[SalaryRead])
def get_employee_salary_detail(
    employee_id: int,
    request: Request,
    current_user: User = Depends(require_any_permission(*SALARY_READ_PERMISSIONS)),
    current_employee: Employee = Depends(get_current_employee),
    service: EmployeeSalaryService = Depends(get_salary_service),
) -> ApiResponse[SalaryRead]:
    salary_data = service.get_employee_salary(
        actor_user_id=current_user.id,
        actor_role=current_user.role,
        actor_permissions=normalize_permissions(current_user.permissions),
        actor_employee_id=current_employee.id,
        target_employee_id=employee_id,
        ip_address=request.client.host if request.client else None,
        user_agent=request.headers.get("user-agent"),
    )
    return ok(SalaryRead.model_validate(salary_data))
