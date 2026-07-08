"""Attendance repository database access."""

from datetime import date
from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.attendance.models import AttendanceRecord, WorkCalendar


class AttendanceRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.db = session

    def get_record(self, employee_id: int, attendance_date: date) -> AttendanceRecord | None:
        return self.session.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date == attendance_date
        ).first()

    def get_records_by_range(self, employee_id: int, start_date: date, end_date: date) -> list[AttendanceRecord]:
        return self.session.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date >= start_date,
            AttendanceRecord.attendance_date <= end_date
        ).order_by(AttendanceRecord.attendance_date.asc()).all()

    def save_record(self, record: AttendanceRecord) -> AttendanceRecord:
        self.session.add(record)
        self.session.commit()
        self.session.refresh(record)
        return record

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


class WorkCalendarRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.db = session

    def get_calendar_by_date(self, calendar_date: date) -> WorkCalendar | None:
        return self.session.query(WorkCalendar).filter(WorkCalendar.calendar_date == calendar_date).first()
