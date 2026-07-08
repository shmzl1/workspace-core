"""Employee payroll route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import current_identity
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.payroll.services.employee_salary_service import EmployeeSalaryService
from app.shared.response import ok

router = APIRouter()


def get_salary_service(session: Session = Depends(get_db_session)) -> EmployeeSalaryService:
    return EmployeeSalaryService.from_session(session)


@router.get("/me")
def my_salary(
    identity: DemoIdentity = Depends(current_identity),
    service: EmployeeSalaryService = Depends(get_salary_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.get_salary_summary(identity, identity.employee_id))


@router.get("/employees/{employee_id}")
def employee_salary(
    employee_id: int,
    identity: DemoIdentity = Depends(current_identity),
    service: EmployeeSalaryService = Depends(get_salary_service),
) -> object:
    return ok(service.get_salary_summary(identity, employee_id))
