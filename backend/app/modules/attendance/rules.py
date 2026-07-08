from datetime import time, datetime, date
from app.modules.attendance.models import WorkCalendar


def calculate_check_in_status(
    check_in_at: datetime,
    calendar: WorkCalendar | None
) -> tuple[str, int]:
    """
    Calculate status and late minutes based on calendar or default settings.
    Default standard check-in: 09:00:00, grace: 0 mins.
    """
    standard_time = time(9, 0)
    grace_minutes = 0

    if calendar:
        # If it is not a workday, it is always NORMAL check-in
        if not calendar.is_workday:
            return "NORMAL", 0
        standard_time = calendar.standard_check_in_time
        grace_minutes = calendar.late_grace_minutes

    check_in_time = check_in_at.time()
    
    # Calculate time difference in minutes
    # Convert standard_time and check_in_time to minutes since midnight for comparison
    standard_minutes = standard_time.hour * 60 + standard_time.minute
    check_in_minutes = check_in_time.hour * 60 + check_in_time.minute

    diff = check_in_minutes - standard_minutes
    if diff > grace_minutes:
        return "LATE", diff
    
    return "NORMAL", 0


def calculate_check_out_status(
    check_out_at: datetime,
    current_status: str,
    calendar: WorkCalendar | None
) -> tuple[str, int]:
    """
    Calculate status and early leave minutes based on calendar or default settings.
    Default standard check-out: 18:00:00.
    """
    standard_time = time(18, 0)

    if calendar:
        if not calendar.is_workday:
            return current_status, 0
        standard_time = calendar.standard_check_out_time

    check_out_time = check_out_at.time()
    
    standard_minutes = standard_time.hour * 60 + standard_time.minute
    check_out_minutes = check_out_time.hour * 60 + check_out_time.minute

    diff = standard_minutes - check_out_minutes
    if diff > 0:
        # If already late, we can choose to keep late, or transition to early leave?
        # Let's say if it's already LATE, it stays LATE, but we record early_leave_minutes.
        # Check constraints: status IN ('NORMAL', 'LATE', 'EARLY_LEAVE', 'ABSENT', 'UNPAID_LEAVE', 'APPROVED_ANNUAL_LEAVE')
        # If status is NORMAL, it becomes EARLY_LEAVE. If LATE, it stays LATE.
        new_status = current_status
        if current_status == "NORMAL":
            new_status = "EARLY_LEAVE"
        return new_status, diff
    
    return current_status, 0
