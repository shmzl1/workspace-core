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
from app.modules.employee.models import Employee, LeaveBalance  # noqa: E402
from app.modules.interview.models import Interview, InterviewSlot, Interviewer, MeetingRoom  # noqa: E402
from app.modules.notification.models import Notification  # noqa: E402
from app.modules.payroll.models import (  # noqa: E402
    PayrollAdjustment,
    PayrollLineItem,
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
            AuditLog,
            Interview,
            InterviewSlot,
            CandidatePipelineRecord,
            PayrollLineItem,
            PayrollReviewRecord,
            PayrollAdjustment,
            CandidateApplication,
            AttendanceRecord,
            SalaryRecord,
            MeetingRoom,
            Interviewer,
            LeaveBalance,
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
