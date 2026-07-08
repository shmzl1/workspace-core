from datetime import date
from sqlalchemy.orm import Session
from app.modules.attendance.models import AttendanceRecord, WorkCalendar


class AttendanceRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_record(self, employee_id: int, attendance_date: date) -> AttendanceRecord | None:
        return self.db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date == attendance_date
        ).first()

    def get_records_by_range(self, employee_id: int, start_date: date, end_date: date) -> list[AttendanceRecord]:
        return self.db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == employee_id,
            AttendanceRecord.attendance_date >= start_date,
            AttendanceRecord.attendance_date <= end_date
        ).order_by(AttendanceRecord.attendance_date.asc()).all()

    def save_record(self, record: AttendanceRecord) -> AttendanceRecord:
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record


class WorkCalendarRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_calendar_by_date(self, calendar_date: date) -> WorkCalendar | None:
        return self.db.query(WorkCalendar).filter(WorkCalendar.calendar_date == calendar_date).first()
