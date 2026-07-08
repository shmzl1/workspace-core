from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session
from app.core.exceptions import TalentFlowError
from app.modules.attendance.models import AttendanceRecord
from app.modules.attendance.repository import AttendanceRepository, WorkCalendarRepository
from app.modules.attendance.rules import calculate_check_in_status, calculate_check_out_status


class AttendanceService:
    def __init__(self, db: Session) -> None:
        self.db = db
        self.repo = AttendanceRepository(db)
        self.calendar_repo = WorkCalendarRepository(db)

    def check_in(self, employee_id: int, check_in_time: datetime, source: str = "WEB") -> AttendanceRecord:
        attendance_date = check_in_time.date()
        calendar = self.calendar_repo.get_calendar_by_date(attendance_date)
        
        record = self.repo.get_record(employee_id, attendance_date)
        if record and record.check_in_at is not None:
            raise TalentFlowError("DUPLICATE_CHECK_IN", "今日已签到，请勿重复签到")

        status, late_mins = calculate_check_in_status(check_in_time, calendar)

        if not record:
            record = AttendanceRecord(
                employee_id=employee_id,
                attendance_date=attendance_date,
                check_in_at=check_in_time,
                status=status,
                late_minutes=late_mins,
                source=source
            )
        else:
            record.check_in_at = check_in_time
            record.status = status
            record.late_minutes = late_mins
            record.source = source

        return self.repo.save_record(record)

    def check_out(self, employee_id: int, check_out_time: datetime, source: str = "WEB") -> AttendanceRecord:
        attendance_date = check_out_time.date()
        calendar = self.calendar_repo.get_calendar_by_date(attendance_date)

        record = self.repo.get_record(employee_id, attendance_date)
        if not record or record.check_in_at is None:
            raise TalentFlowError("CHECK_IN_REQUIRED", "今日未签到，无法签退")

        if record.check_out_at is not None:
            raise TalentFlowError("DUPLICATE_CHECK_OUT", "今日已签退，请勿重复签退")

        status, early_mins = calculate_check_out_status(check_out_time, record.status, calendar)

        record.check_out_at = check_out_time
        record.status = status
        record.early_leave_minutes = early_mins
        record.source = source

        return self.repo.save_record(record)

    def get_today_attendance(self, employee_id: int, today_date: date) -> AttendanceRecord | None:
        return self.repo.get_record(employee_id, today_date)

    def get_weekly_summary(self, employee_id: int, today_date: date) -> list[AttendanceRecord]:
        # Calculate Monday and Sunday of this week
        monday = today_date - timedelta(days=today_date.weekday())
        sunday = monday + timedelta(days=6)
        
        # We fetch all records for this employee within this date range
        db_records = self.repo.get_records_by_range(employee_id, monday, sunday)
        
        # We want to fill in default records for any missing days of the week up to today
        # so the frontend shows correct status
        record_map = {r.attendance_date: r for r in db_records}
        results = []
        
        for i in range(7):
            day = monday + timedelta(days=i)
            if day in record_map:
                results.append(record_map[day])
            else:
                # If it's a future day or a day without records, return a stub record
                # Check calendar to see if it's a workday
                cal = self.calendar_repo.get_calendar_by_date(day)
                is_workday = cal.is_workday if cal else (day.weekday() < 5)
                
                status = "ABSENT" if (is_workday and day < today_date) else "NORMAL"
                # If it's a weekend and not a workday, it is normal
                if not is_workday:
                    status = "NORMAL"
                
                results.append(AttendanceRecord(
                    employee_id=employee_id,
                    attendance_date=day,
                    status=status,
                    late_minutes=0,
                    early_leave_minutes=0,
                    source="WEB",
                    remark="Auto-generated summary stub"
                ))
                
        return results
