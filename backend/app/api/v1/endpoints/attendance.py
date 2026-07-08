"""Attendance route boundary."""

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, current_identity
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity
from app.modules.attendance.schemas import (
    AttendanceRecordRead,
    CheckInResponse,
    CheckOutResponse,
    WeeklyAttendanceSummary,
)
from app.modules.attendance.service import AttendanceService
from app.employee.models import Employee  # Alias target or dynamic import if needed
from app.modules.employee.models import Employee
from app.shared.response import ApiResponse, ok

router = APIRouter()


def get_attendance_service(session: Session = Depends(get_db_session)) -> AttendanceService:
    return AttendanceService.from_session(session)


@router.get("/today", response_model=ApiResponse[AttendanceRecordRead | None])
def get_today(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[AttendanceRecordRead | None]:
    """Retrieve today's attendance record for the logged-in employee."""
    service = AttendanceService(db)
    record = service.get_today_attendance(current_employee.id, date.today())
    if record:
        return ok(AttendanceRecordRead.model_validate(record))
    return ok(None)


@router.post("/check-in", response_model=ApiResponse[CheckInResponse])
def check_in(
    source: str = Query(default="WEB", description="Source of the request: WEB, MINIPROGRAM"),
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[CheckInResponse]:
    """Perform today's check-in."""
    service = AttendanceService(db)
    record = service.check_in(current_employee.id, datetime.now(), source)
    data = CheckInResponse(
        message="签到成功",
        record=AttendanceRecordRead.model_validate(record)
    )
    return ok(data)


@router.post("/check-out", response_model=ApiResponse[CheckOutResponse])
def check_out(
    source: str = Query(default="WEB", description="Source of the request: WEB, MINIPROGRAM"),
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[CheckOutResponse]:
    """Perform today's check-out."""
    service = AttendanceService(db)
    record = service.check_out(current_employee.id, datetime.now(), source)
    data = CheckOutResponse(
        message="签退成功",
        record=AttendanceRecordRead.model_validate(record)
    )
    return ok(data)


@router.get("/weekly", response_model=ApiResponse[list[WeeklyAttendanceSummary]])
def get_weekly(
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[list[WeeklyAttendanceSummary]]:
    """Retrieve weekly attendance summary for the logged-in employee."""
    service = AttendanceService(db)
    records = service.get_weekly_summary(current_employee.id, date.today())
    data = [
        WeeklyAttendanceSummary(
            attendance_date=r.attendance_date,
            status=r.status,
            check_in_at=r.check_in_at,
            check_out_at=r.check_out_at,
        )
        for r in records
    ]
    return ok(data)


@router.get("/records")
def records(
    limit: int = 31,
    identity: DemoIdentity = Depends(current_identity),
    service: AttendanceService = Depends(get_attendance_service),
) -> object:
    if identity.employee_id is None:
        raise TalentFlowError("EMPLOYEE_CONTEXT_REQUIRED", "当前演示身份缺少 employee_id", 401)
    return ok(service.list_recent(identity.employee_id, limit))
