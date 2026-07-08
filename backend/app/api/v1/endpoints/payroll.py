"""Payroll route boundary."""

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, get_current_user
from app.core.exceptions import TalentFlowError
from app.modules.auth.models import User
from app.modules.employee.models import Employee
from app.modules.payroll.schemas.salary import SalaryRead
from app.modules.payroll.services.employee_salary_service import EmployeeSalaryService
from app.shared.response import ApiResponse, ok

router = APIRouter()


@router.get("/me", response_model=ApiResponse[SalaryRead])
def get_my_salary(
    request: Request,
    current_user: User = Depends(get_current_user),
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[SalaryRead]:
    """Retrieve current logged-in employee's own salary details."""
    service = EmployeeSalaryService(db)
    
    # Extract request metadata for audit logging
    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    salary_data = service.get_employee_salary(
        actor_user_id=current_user.id,
        actor_role=current_user.role,
        actor_employee_id=current_employee.id,
        target_employee_id=current_employee.id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return ok(SalaryRead.model_validate(salary_data))


@router.get("/employee/{employee_id}", response_model=ApiResponse[SalaryRead])
def get_employee_salary(
    employee_id: int,
    request: Request,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ApiResponse[SalaryRead]:
    """Retrieve specified employee's salary details. Restricted based on role permissions."""
    service = EmployeeSalaryService(db)
    
    # Try to resolve employee record for the actor, if exists (Admins might not have one)
    actor_employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    actor_employee_id = actor_employee.id if actor_employee else None

    ip_address = request.client.host if request.client else None
    user_agent = request.headers.get("user-agent")

    salary_data = service.get_employee_salary(
        actor_user_id=current_user.id,
        actor_role=current_user.role,
        actor_employee_id=actor_employee_id,
        target_employee_id=employee_id,
        ip_address=ip_address,
        user_agent=user_agent
    )
    return ok(SalaryRead.model_validate(salary_data))
