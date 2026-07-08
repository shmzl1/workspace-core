"""Employee route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee
from app.modules.employee.models import Employee
from app.modules.employee.schemas import EmployeeProfileResponse, EmployeeRead, LeaveBalanceRead
from app.modules.employee.service import EmployeeService
from app.shared.response import ApiResponse, ok

router = APIRouter()


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
