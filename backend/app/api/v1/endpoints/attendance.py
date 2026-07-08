"""Attendance route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import current_identity
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.attendance.service import AttendanceService
from app.shared.response import ok

router = APIRouter()


def get_attendance_service(session: Session = Depends(get_db_session)) -> AttendanceService:
    return AttendanceService.from_session(session)


@router.get("/today")
def today(
    identity: DemoIdentity = Depends(current_identity),
    service: AttendanceService = Depends(get_attendance_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.get_today(identity.employee_id))


@router.get("/records")
def records(
    limit: int = 31,
    identity: DemoIdentity = Depends(current_identity),
    service: AttendanceService = Depends(get_attendance_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.list_recent(identity.employee_id, limit))
