"""Attendance repository database access."""

from datetime import date

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.attendance.models import AttendanceRecord


class AttendanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_daily_record(self, employee_id: int, attendance_date: date) -> AttendanceRecord | None:
        return self.session.scalar(
            select(AttendanceRecord).where(
                AttendanceRecord.employee_id == employee_id,
                AttendanceRecord.attendance_date == attendance_date,
            )
        )

    def list_records(self, employee_id: int, limit: int = 31) -> list[AttendanceRecord]:
        return list(
            self.session.scalars(
                select(AttendanceRecord)
                .where(AttendanceRecord.employee_id == employee_id)
                .order_by(AttendanceRecord.attendance_date.desc())
                .limit(limit)
            )
        )
