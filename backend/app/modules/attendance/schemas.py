from datetime import date, datetime
from pydantic import BaseModel, ConfigDict


class AttendanceRecordRead(BaseModel):
    id: int
    employee_id: int
    attendance_date: date
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
    status: str
    late_minutes: int
    early_leave_minutes: int
    leave_balance_id: int | None = None
    source: str
    remark: str | None = None

    model_config = ConfigDict(from_attributes=True)


class CheckInResponse(BaseModel):
    message: str
    record: AttendanceRecordRead


class CheckOutResponse(BaseModel):
    message: str
    record: AttendanceRecordRead


class WeeklyAttendanceSummary(BaseModel):
    attendance_date: date
    status: str
    check_in_at: datetime | None = None
    check_out_at: datetime | None = None
