"""Attendance route boundary."""

from datetime import date, datetime
from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, get_current_user, require_permission, user_permissions
from app.core.exceptions import TalentFlowError
from app.modules.auth.models import User
from app.modules.attendance.schemas import (
    AttendanceRecordRead,
    CheckInResponse,
    CheckOutResponse,
    WeeklyAttendanceSummary,
    MonthlyAttendanceSummaryRead,
)
from app.modules.attendance.service import AttendanceService
from app.modules.employee.models import Employee
from app.shared.response import ApiResponse, ok

router = APIRouter()


def get_attendance_service(session: Session = Depends(get_db_session)) -> AttendanceService:
    return AttendanceService.from_session(session)



@router.get("/today", response_model=ApiResponse[AttendanceRecordRead | None])
def get_today(
    current_employee: Employee = Depends(get_current_employee),
    _=Depends(require_permission("attendance.self.read")),
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
    _=Depends(require_permission("attendance.self.manage")),
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
    _=Depends(require_permission("attendance.self.manage")),
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
    _=Depends(require_permission("attendance.self.read")),
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


@router.get("/monthly", response_model=ApiResponse[MonthlyAttendanceSummaryRead])
def get_monthly(
    year: int = Query(..., ge=2000, le=2100),
    month: int = Query(..., ge=1, le=12),
    employee_id: int | None = Query(None),
    current_user: User = Depends(get_current_user),
    current_employee: Employee = Depends(get_current_employee),
    db: Session = Depends(get_db_session),
) -> ApiResponse[MonthlyAttendanceSummaryRead]:
    """Retrieve monthly attendance summary with permission boundary checks."""
    target_id = employee_id or current_employee.id

    if target_id != current_employee.id:
        permissions = user_permissions(current_user)
        has_admin_read = "payroll.all.read" in permissions or "payroll.review.read" in permissions or "audit.read" in permissions
        
        has_dept_read = False
        if "employee.department.read" in permissions:
            target_emp = db.get(Employee, target_id)
            if target_emp and target_emp.department == current_employee.department:
                has_dept_read = True

        if not (has_admin_read or has_dept_read):
            raise TalentFlowError("PERMISSION_DENIED", "您没有权限查看该员工的月度考勤汇总。", 403)

    service = AttendanceService(db)
    summary = service.get_monthly_summary(target_id, year, month)
    return ok(MonthlyAttendanceSummaryRead.model_validate(summary))


@router.get("/records")
def records(
    limit: int = 31,
    current_employee: Employee = Depends(get_current_employee),
    _=Depends(require_permission("attendance.self.read")),
    service: AttendanceService = Depends(get_attendance_service),
) -> object:
    return ok(service.list_recent(current_employee.id, limit))
