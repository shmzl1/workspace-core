"""Load repeatable Sprint 1 demo data into PostgreSQL.

This script expects the backend dependencies and DATABASE_URL/.env settings to
be available. It uses only fictional demo records from data/seed.
"""

from __future__ import annotations

import json
import sys
from datetime import date, datetime
from decimal import Decimal
from pathlib import Path
from typing import Any

from sqlalchemy import delete

ROOT = Path(__file__).resolve().parents[1]
BACKEND = ROOT / "backend"
if str(BACKEND) not in sys.path:
    sys.path.insert(0, str(BACKEND))

from app.core.database import SessionLocal  # noqa: E402
from app.modules.attendance.models import AttendanceRecord  # noqa: E402
from app.modules.audit.models import AuditLog  # noqa: E402
from app.modules.auth.models import User  # noqa: E402
from app.modules.employee.models import Employee, LeaveBalance, LeaveRequest  # noqa: E402
from app.modules.interview.models import Interview, InterviewSlot, Interviewer, MeetingRoom  # noqa: E402
from app.modules.notification.models import Notification  # noqa: E402
from app.modules.policy.models import PolicyDocument  # noqa: E402
from app.modules.payroll.models import (  # noqa: E402
    PayrollAdjustment,
    PayrollLineItem,
    PayrollPeriod,
    PayrollReviewRecord,
    SalaryRecord,
)
from app.modules.recruitment.models import Candidate, CandidateApplication, CandidatePipelineRecord, Job  # noqa: E402

SEED_DIR = ROOT / "data" / "seed"


def load_json(name: str) -> list[dict[str, Any]]:
    with (SEED_DIR / name).open("r", encoding="utf-8") as file:
        return json.load(file)


def parse_value(value: Any) -> Any:
    if isinstance(value, str):
        if value.endswith("+08:00") or "T" in value:
            return datetime.fromisoformat(value)
        if len(value) == 10 and value[4] == "-" and value[7] == "-":
            return date.fromisoformat(value)
        if value.count(".") == 1 and value.replace(".", "").isdigit():
            return Decimal(value)
    return value


def rows(name: str) -> list[dict[str, Any]]:
    return [{key: parse_value(value) for key, value in row.items()} for row in load_json(name)]


def reset_demo_data() -> None:
    with SessionLocal() as session:
        for model in (
            Notification,
            LeaveRequest,
            AuditLog,
            Interview,
            InterviewSlot,
            CandidatePipelineRecord,
            PayrollLineItem,
            PayrollReviewRecord,
            PayrollPeriod,
            PayrollAdjustment,
            CandidateApplication,
            AttendanceRecord,
            SalaryRecord,
            MeetingRoom,
            Interviewer,
            LeaveBalance,
            PolicyDocument,
            Candidate,
            Job,
            Employee,
            User,
        ):
            session.execute(delete(model))

        for model, file_name in (
            (User, "users.json"),
            (Employee, "employees.json"),
            (LeaveBalance, "leave_balances.json"),
            (PolicyDocument, "policy_documents.json"),
            (Job, "jobs.json"),
            (Candidate, "candidates.json"),
            (Interviewer, "interviewers.json"),
            (MeetingRoom, "meeting_rooms.json"),
            (SalaryRecord, "salary_records.json"),
            (AttendanceRecord, "attendance_records.json"),
        ):
            session.add_all(model(**row) for row in rows(file_name))

        session.add_all(
            [
                PayrollPeriod(
                    id=1, period_code="2026-07", start_date=date(2026, 7, 1), end_date=date(2026, 7, 31),
                    standard_work_days=Decimal("23"), status="OPEN",
                ),
                LeaveRequest(
                    id=1, employee_id=2, leave_type="ANNUAL", start_at=datetime.fromisoformat("2026-06-20T09:00:00+08:00"),
                    end_at=datetime.fromisoformat("2026-06-21T18:00:00+08:00"), duration_hours=Decimal("16"), status="APPROVED",
                ),
                LeaveRequest(
                    id=2, employee_id=2, leave_type="SICK", start_at=datetime.fromisoformat("2026-05-08T09:00:00+08:00"),
                    end_at=datetime.fromisoformat("2026-05-08T18:00:00+08:00"), duration_hours=Decimal("8"), status="APPROVED",
                ),
                PayrollReviewRecord(
                    id=1, employee_id=2, payroll_period_id=1, salary_record_id=1,
                    status="PENDING_HR_CONFIRMATION", base_salary_snapshot=Decimal("12000.00"),
                    standard_work_days_snapshot=Decimal("23"), calculation_snapshot={"source": "seed", "note": "演示预审记录"},
                    total_earnings=Decimal("12000.00"), total_deductions=Decimal("100.00"), net_salary_preview=Decimal("11900.00"), generated_by_user_id=4,
                ),
                PayrollReviewRecord(
                    id=2, employee_id=3, payroll_period_id=1, salary_record_id=2,
                    status="PRE_AUDIT_GENERATED", base_salary_snapshot=Decimal("22000.00"),
                    standard_work_days_snapshot=Decimal("23"), calculation_snapshot={"source": "seed", "note": "演示预审记录"},
                    total_earnings=Decimal("22000.00"), total_deductions=Decimal("0.00"), net_salary_preview=Decimal("22000.00"), generated_by_user_id=4,
                ),
                CandidateApplication(
                    id=1,
                    candidate_id=1,
                    job_id=1,
                    current_stage="AI_SCREENED",
                    score_total=Decimal("88.50"),
                    score_breakdown={"skill": 36, "project": 32, "experience": 20.5},
                    weights_snapshot={"skill": 0.4, "project": 0.35, "experience": 0.25},
                ),
                CandidateApplication(
                    id=2,
                    candidate_id=2,
                    job_id=1,
                    current_stage="AI_SCREENED",
                    score_total=Decimal("82.00"),
                    score_breakdown={"skill": 31, "project": 27, "experience": 24},
                    weights_snapshot={"skill": 0.4, "project": 0.35, "experience": 0.25},
                ),
                CandidateApplication(
                    id=3,
                    candidate_id=3,
                    job_id=1,
                    current_stage="APPLIED",
                    score_total=Decimal("76.50"),
                    score_breakdown={"skill": 34, "project": 24, "experience": 18.5},
                    weights_snapshot={"skill": 0.4, "project": 0.35, "experience": 0.25},
                ),
            ]
        )

        session.commit()


if __name__ == "__main__":
    reset_demo_data()
    print("Demo seed data has been rebuilt.")
