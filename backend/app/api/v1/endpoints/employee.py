"""Employee route boundary."""

from datetime import date

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import current_identity
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.employee.service import EmployeeService
from app.shared.response import ok

router = APIRouter()


def get_employee_service(session: Session = Depends(get_db_session)) -> EmployeeService:
    return EmployeeService.from_session(session)


@router.get("")
def list_employees(service: EmployeeService = Depends(get_employee_service)) -> object:
    return ok(service.list_employees())


@router.get("/me")
def get_me(
    identity: DemoIdentity = Depends(current_identity),
    service: EmployeeService = Depends(get_employee_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.get_employee(identity.employee_id))


@router.get("/me/leave-balance")
def get_my_leave_balance(
    year: int | None = None,
    identity: DemoIdentity = Depends(current_identity),
    service: EmployeeService = Depends(get_employee_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.get_annual_leave(identity.employee_id, year or date.today().year))
