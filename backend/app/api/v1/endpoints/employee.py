"""Employee route boundary."""

from datetime import date
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, current_identity
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.employee.models import Employee
from app.modules.employee.schemas import EmployeeProfileResponse, EmployeeRead, LeaveBalanceRead
from app.modules.employee.service import EmployeeService
from app.shared.response import ApiResponse, ok

router = APIRouter()


def get_employee_service(session: Session = Depends(get_db_session)) -> EmployeeService:
    return EmployeeService.from_session(session)


@router.get("")
def list_employees(service: EmployeeService = Depends(get_employee_service)) -> object:
    return ok(service.list_employees())


@router.get("/me", response_model=ApiResponse[EmployeeProfileResponse])
def get_me(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[EmployeeProfileResponse]:
    """Retrieve personal employee profile information including leave balances."""
    service = EmployeeService(db)
    balance = service.get_employee_leave_balance(current_employee.id, 2026)
    
    return ok(
        EmployeeProfileResponse(
            employee=EmployeeRead.model_validate(current_employee),
            leave_balance=LeaveBalanceRead.model_validate(balance) if balance else None
        )
    )


@router.get("/me/leave-balance")
def get_my_leave_balance(
    year: int | None = None,
    identity: DemoIdentity = Depends(current_identity),
    service: EmployeeService = Depends(get_employee_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.get_annual_leave(identity.employee_id, year or date.today().year))
