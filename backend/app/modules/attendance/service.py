"""Attendance service for API-facing reads."""

from datetime import date

from app.modules._serialization import model_to_dict
from app.modules.attendance.repository import AttendanceRepository
from sqlalchemy.orm import Session


ATTENDANCE_FIELDS = [
    "id",
    "employee_id",
    "attendance_date",
    "check_in_at",
    "check_out_at",
    "status",
    "late_minutes",
    "early_leave_minutes",
    "source",
    "remark",
]


class AttendanceService:
    def __init__(self, repository: AttendanceRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "AttendanceService":
        return cls(AttendanceRepository(session))

    def get_today(self, employee_id: int, today: date | None = None) -> dict | None:
        record = self.repository.get_daily_record(employee_id, today or date.today())
        return model_to_dict(record, ATTENDANCE_FIELDS) if record else None

    def list_recent(self, employee_id: int, limit: int = 31) -> list[dict]:
        return [model_to_dict(record, ATTENDANCE_FIELDS) for record in self.repository.list_records(employee_id, limit)]
