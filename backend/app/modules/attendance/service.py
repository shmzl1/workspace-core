"""Attendance service for read/write attendance operations."""

from datetime import date, datetime, timedelta
from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.attendance.models import AttendanceRecord
from app.modules.attendance.repository import AttendanceRepository, WorkCalendarRepository
from app.modules.attendance.rules import calculate_check_in_status, calculate_check_out_status

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
    def __init__(self, repository_or_session) -> None:
        if isinstance(repository_or_session, Session):
            self.repository = AttendanceRepository(repository_or_session)
            self.db = repository_or_session
        else:
            self.repository = repository_or_session
            self.db = repository_or_session.session
        
        self.repo = self.repository
        self.calendar_repo = WorkCalendarRepository(self.db)

    @classmethod
    def from_session(cls, session: Session) -> "AttendanceService":
        return cls(AttendanceRepository(session))

    def check_in(self, employee_id: int, check_in_time: datetime, source: str = "WEB") -> AttendanceRecord:
        attendance_date = check_in_time.date()
        calendar = self.calendar_repo.get_calendar_by_date(attendance_date)
        if calendar is None:
            raise TalentFlowError("WORK_CALENDAR_NOT_FOUND", "今日工作日历尚未配置，无法签到。")
        if not calendar.is_workday:
            raise TalentFlowError("NOT_A_WORKDAY", "今日不是工作日，无需签到。")
        
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
        if calendar is None:
            raise TalentFlowError("WORK_CALENDAR_NOT_FOUND", "今日工作日历尚未配置，无法签退。")
        if not calendar.is_workday:
            raise TalentFlowError("NOT_A_WORKDAY", "今日不是工作日，无需签退。")

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

    def get_today(self, employee_id: int, today: date | None = None) -> dict | None:
        record = self.repository.get_daily_record(employee_id, today or date.today())
        return model_to_dict(record, ATTENDANCE_FIELDS) if record else None

    def list_recent(self, employee_id: int, limit: int = 31) -> list[dict]:
        return [model_to_dict(record, ATTENDANCE_FIELDS) for record in self.repository.list_records(employee_id, limit)]

    def get_monthly_summary(self, employee_id: int, year: int, month: int) -> dict:
        import calendar
        from decimal import Decimal
        from app.modules.employee.models import LeaveBalance

        last_day = calendar.monthrange(year, month)[1]
        start_date = date(year, month, 1)
        end_date = date(year, month, last_day)

        records = self.repo.get_records_by_range(employee_id, start_date, end_date)

        late_count = 0
        total_late_minutes = 0
        early_leave_count = 0
        total_early_leave_minutes = 0
        absent_count = 0
        unpaid_leave_count = 0
        approved_annual_leave_count = 0
        normal_count = 0

        for r in records:
            if r.status == "NORMAL":
                normal_count += 1
            elif r.status == "LATE":
                late_count += 1
                total_late_minutes += r.late_minutes
            elif r.status == "EARLY_LEAVE":
                early_leave_count += 1
                total_early_leave_minutes += r.early_leave_minutes
            elif r.status == "ABSENT":
                absent_count += 1
            elif r.status == "UNPAID_LEAVE":
                unpaid_leave_count += 1
            elif r.status == "APPROVED_ANNUAL_LEAVE":
                approved_annual_leave_count += 1

        balance = self.db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == year,
            LeaveBalance.leave_type == "ANNUAL"
        ).first()

        total_days = balance.total_days if balance else Decimal("0")
        used_days = balance.used_days if balance else Decimal("0")
        remaining_days = total_days - used_days

        return {
            "employee_id": employee_id,
            "year": year,
            "month": month,
            "late_count": late_count,
            "total_late_minutes": total_late_minutes,
            "early_leave_count": early_leave_count,
            "total_early_leave_minutes": total_early_leave_minutes,
            "absent_count": absent_count,
            "unpaid_leave_count": unpaid_leave_count,
            "approved_annual_leave_count": approved_annual_leave_count,
            "normal_count": normal_count,
            "total_days": total_days,
            "used_days": used_days,
            "remaining_days": remaining_days,
        }

