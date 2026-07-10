"""Create repeatable local Sprint 1 acceptance data."""

from __future__ import annotations

import os
import sys
import traceback
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base, SessionLocal
from app.modules import model_registry  # noqa: F401
from app.modules.attendance.models import AttendanceRecord, WorkCalendar
from app.modules.audit.models import AuditLog
from app.modules.auth.models import User
from app.modules.employee.models import Employee, LeaveBalance
from app.modules.interview.models import Interview, Interviewer, InterviewSlot, MeetingRoom
from app.modules.payroll.models import PayrollLineItem, PayrollPeriod, PayrollReviewRecord, SalaryRecord
from app.modules.recruitment.models import Candidate, CandidateApplication, CandidatePipelineRecord, Job

CLEAR_ORDER = [
    "payroll_line_items", "audit_logs", "notifications", "interviews", "interview_slots",
    "candidate_pipeline_records", "payroll_review_records", "payroll_adjustments", "payroll_rules",
    "salary_records", "payroll_periods", "interviewers", "meeting_rooms",
    "candidate_applications", "candidates", "jobs", "attendance_records", "work_calendars",
    "leave_balances", "policy_documents", "employees", "users",
]


def log(stage: str) -> None:
    print(f"[seed] {stage}", flush=True)


def masked_database_url(url: str) -> str:
    parsed = urlsplit(url)
    port = f":{parsed.port}" if parsed.port else ""
    credentials = f"{parsed.username}:***@" if parsed.username else ""
    return urlunsplit((parsed.scheme, f"{credentials}{parsed.hostname or ''}{port}", parsed.path, "", ""))


def clear_existing_data(db: Session) -> None:
    for table_name in CLEAR_ORDER:
        table = Base.metadata.tables.get(table_name)
        if table is not None:
            db.execute(table.delete())
    db.commit()


def add_users(db: Session, password_hash: str) -> None:
    db.add_all([
        User(id=1, username="zhangwei", password_hash=password_hash, role="EMPLOYEE"),
        User(id=2, username="liming", password_hash=password_hash, role="DEPARTMENT_MANAGER"),
        User(id=3, username="linyuqing", password_hash=password_hash, role="HR_SPECIALIST"),
        User(id=4, username="wangqiang", password_hash=password_hash, role="PAYROLL_ADMIN"),
    ])
    db.commit()


def add_employees(db: Session, today: date) -> None:
    db.add_all([
        Employee(id=2, user_id=2, employee_no="EMP002", full_name="李明", department="研发部",
                 job_title="研发经理", email="liming@example.test", hire_date=today - timedelta(days=1200)),
        Employee(id=3, user_id=3, employee_no="EMP003", full_name="林雨晴", department="人力资源部",
                 job_title="HR 专员", email="linyuqing@example.test", hire_date=today - timedelta(days=700)),
        Employee(id=4, user_id=4, employee_no="EMP004", full_name="王强", department="财务部",
                 job_title="薪酬管理员", email="wangqiang@example.test", hire_date=today - timedelta(days=900)),
    ])
    db.flush()
    db.add(Employee(id=1, user_id=1, employee_no="EMP001", full_name="张伟", department="研发部",
                    job_title="高级开发工程师", manager_employee_id=2, email="zhangwei@example.test",
                    hire_date=today - timedelta(days=500)))
    db.add_all([
        LeaveBalance(employee_id=employee_id, leave_type="ANNUAL", year=today.year,
                     total_days=days, used_days=0)
        for employee_id, days in [(1, 10), (2, 15), (3, 10), (4, 10)]
    ])
    db.commit()


def add_recruitment(db: Session, today: date) -> None:
    log("写入招聘岗位")
    db.add_all([
        Job(id=1, job_code="JOB-BE-001", title="后端开发工程师", department="研发部",
            description="负责 FastAPI 业务模块开发。", required_skills=["Python", "FastAPI", "PostgreSQL"],
            preferred_skills=["Vue", "Docker"], min_experience_months=24, location="上海",
            employment_type="FULL_TIME", status="OPEN", owner_user_id=3),
        Job(id=2, job_code="JOB-FE-001", title="前端开发工程师", department="产品技术部",
            description="负责 Vue 管理端开发。", required_skills=["Vue", "TypeScript"],
            preferred_skills=["Vite", "Tailwind CSS"], min_experience_months=18, location="杭州",
            employment_type="FULL_TIME", status="OPEN", owner_user_id=3),
    ])
    candidates = [
        ("CAN001", "陈晨", "chenchen", ["Python", "FastAPI", "PostgreSQL"], 36, 14, "三年 Python 后端经验。"),
        ("CAN002", "周晓", "zhouxiao", ["Vue", "TypeScript", "Vite"], 30, 21, "Vue 3 项目经验。"),
        ("CAN003", "吴桐", "wutong", ["Python", "SQL"], 20, 7, "熟悉 Python 与数据库开发。"),
        ("CAN004", "赵宁", "zhaoning", ["JavaScript", "Vue"], 16, 30, "前端工程化实践。"),
    ]
    log("写入候选人")
    db.add_all([
        Candidate(id=index, candidate_no=no, full_name=name, email=f"{mail}@example.test",
                  skills=skills, experience_months=months, available_from=today + timedelta(days=delay),
                  source="SEED", resume_text=resume,
                  profile_json={"education": "本科", "projects": ["企业应用项目"]})
        for index, (no, name, mail, skills, months, delay, resume) in enumerate(candidates, 1)
    ])
    db.flush()
    log("写入候选人申请")
    db.add_all([
        CandidateApplication(
            id=1, candidate_id=1, job_id=1, current_stage="INTERVIEW_PENDING",
            score_total=Decimal("91"), score_breakdown={
                "skill": 96, "experience": 90, "project": 88, "education": 82,
                "risk": 92, "match_score": 94, "overall_score": 91,
            }, weights_snapshot={"skill": 0.3, "experience": 0.2, "project": 0.25, "education": 0.1, "risk": 0.15},
            scored_at=datetime.now().astimezone(),
        ),
        CandidateApplication(
            id=2, candidate_id=2, job_id=2, current_stage="AI_SCREENED",
            score_total=Decimal("84"), score_breakdown={
                "skill": 90, "experience": 82, "project": 80, "education": 78,
                "risk": 85, "match_score": 88, "overall_score": 84,
            }, weights_snapshot={"skill": 0.3, "experience": 0.2, "project": 0.25, "education": 0.1, "risk": 0.15},
            scored_at=datetime.now().astimezone(),
        ),
        CandidateApplication(id=3, candidate_id=3, job_id=1, current_stage="OFFERED"),
        CandidateApplication(id=4, candidate_id=4, job_id=2, current_stage="HIRED"),
    ])
    db.flush()
    db.add_all([
        CandidatePipelineRecord(application_id=1, from_stage=None, to_stage="INTERVIEW_PENDING", note="初始化招聘阶段"),
        CandidatePipelineRecord(application_id=2, from_stage=None, to_stage="AI_SCREENED", note="初始化招聘阶段"),
        CandidatePipelineRecord(application_id=3, from_stage=None, to_stage="OFFERED", note="初始化招聘阶段"),
        CandidatePipelineRecord(application_id=4, from_stage=None, to_stage="HIRED", note="初始化招聘阶段"),
    ])
    db.commit()


def add_interviews(db: Session, now: datetime) -> None:
    start = now.replace(hour=14, minute=0, second=0, microsecond=0)
    end = start + timedelta(hours=1)
    log("写入面试官")
    db.add_all([
        Interviewer(id=1, employee_id=2, specialties=["Python", "系统设计"], max_interviews_per_day=4),
        Interviewer(id=2, employee_id=3, specialties=["沟通能力", "文化匹配"], max_interviews_per_day=5),
    ])
    log("写入会议室")
    db.add_all([
        MeetingRoom(id=1, room_code="R-A101", name="A101 会议室", location="上海办公室", capacity=6),
        MeetingRoom(id=2, room_code="R-B201", name="B201 会议室", location="上海办公室", capacity=8),
    ])
    db.flush()
    log("写入面试数据")
    db.add_all([
        InterviewSlot(resource_type="CANDIDATE", candidate_id=1, start_at=start, end_at=end),
        InterviewSlot(resource_type="INTERVIEWER", interviewer_id=1, start_at=start, end_at=end),
        InterviewSlot(resource_type="ROOM", meeting_room_id=2, start_at=start, end_at=end),
        Interview(application_id=2, interviewer_id=2, meeting_room_id=1, start_at=start, end_at=end,
                  status="SCHEDULED", conflict_explanation={"note": "用于验证会议室冲突检测"},
                  created_by_user_id=3),
    ])
    db.commit()


def add_attendance(db: Session, today: date, now: datetime) -> None:
    log("写入工作日历")
    for offset in range(-7, 8):
        day = today + timedelta(days=offset)
        workday = day.weekday() < 5 or day == today
        db.add(WorkCalendar(calendar_date=day, is_workday=workday, standard_check_in_time=time(9),
                            standard_check_out_time=time(18), late_grace_minutes=10,
                            holiday_name=None if workday else "周末"))
    history_day = today - timedelta(days=1)
    log("写入考勤记录")
    db.add(AttendanceRecord(
        employee_id=2, attendance_date=history_day,
        check_in_at=now.replace(year=history_day.year, month=history_day.month, day=history_day.day,
                                hour=8, minute=55),
        check_out_at=now.replace(year=history_day.year, month=history_day.month, day=history_day.day,
                                 hour=18, minute=5),
        status="NORMAL", source="SEED",
    ))
    db.commit()


def add_payroll(db: Session, today: date) -> None:
    log("写入薪资记录")
    amounts = ["25000", "35000", "18000", "20000"]
    salaries = [
        SalaryRecord(id=index, employee_id=index, base_salary=Decimal(amount),
                     effective_from=date(today.year, 1, 1), created_by_user_id=4)
        for index, amount in enumerate(amounts, 1)
    ]
    period_start = today.replace(day=1)
    next_month = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    db.add_all([*salaries, PayrollPeriod(
        id=1, period_code=period_start.strftime("%Y-%m"), start_date=period_start,
        end_date=next_month - timedelta(days=1), standard_work_days=Decimal("22"), status="OPEN",
    )])
    db.flush()
    reviews = [
        PayrollReviewRecord(
            id=index, employee_id=index, payroll_period_id=1, salary_record_id=index,
            status="PENDING_HR_CONFIRMATION", base_salary_snapshot=Decimal(amount),
            standard_work_days_snapshot=Decimal("22"), calculation_snapshot={"source": "seed"},
            total_earnings=Decimal(amount), total_deductions=Decimal("0"),
            net_salary_preview=Decimal(amount), generated_by_user_id=4,
        )
        for index, amount in enumerate(amounts, 1)
    ]
    db.add_all(reviews)
    db.flush()
    db.add_all([
        PayrollLineItem(payroll_review_record_id=item.id, item_type="EARNING", item_name="基本工资",
                        amount=item.base_salary_snapshot, source_type="RULE",
                        source_reference_json={"salary_record_id": item.salary_record_id},
                        calculation_detail_json={"formula": "月度基本工资"})
        for item in reviews
    ])
    db.commit()


def add_audit_logs(db: Session) -> None:
    log("写入权限审计日志")
    rows = [
        (1, "EMPLOYEE", 1, "ALLOWED", "员工查看本人薪资"),
        (1, "EMPLOYEE", 2, "DENIED", "员工不能查看他人薪资"),
        (3, "HR_SPECIALIST", 1, "ALLOWED", "HR 按规则查看薪资"),
        (4, "PAYROLL_ADMIN", 2, "ALLOWED", "薪酬管理员查看薪资明细"),
        (2, "DEPARTMENT_MANAGER", 1, "ALLOWED", "部门经理查看本部门有限字段"),
    ]
    db.add_all([
        AuditLog(actor_user_id=user_id, actor_role=role, target_employee_id=target_id,
                 action="QUERY_SALARY", resource_type="SALARY", resource_id=target_id,
                 requested_fields=["base_salary", "currency", "effective_from", "effective_to"],
                 result=result, reason=reason, trace_id=f"seed-{index:03d}")
        for index, (user_id, role, target_id, result, reason) in enumerate(rows, 1)
    ])
    db.commit()


def seed_data() -> None:
    settings = get_settings()
    print(f"[seed] DATABASE_URL={masked_database_url(settings.database_url)}", flush=True)
    current_stage = "初始化"
    db = SessionLocal()
    try:
        today = date.today()
        now = datetime.now().astimezone()
        current_stage = "清理旧数据"
        log(current_stage)
        clear_existing_data(db)
        password_hash = bcrypt.hash("password")
        stages = [
            ("写入用户", lambda: add_users(db, password_hash)),
            ("写入员工", lambda: add_employees(db, today)),
            ("写入招聘岗位、候选人和候选人申请", lambda: add_recruitment(db, today)),
            ("写入面试官、会议室和面试数据", lambda: add_interviews(db, now)),
            ("写入考勤日历和考勤记录", lambda: add_attendance(db, today, now)),
            ("写入薪资记录、薪资预审记录和明细项", lambda: add_payroll(db, today)),
            ("写入审计日志", lambda: add_audit_logs(db)),
        ]
        for current_stage, operation in stages:
            log(current_stage)
            operation()
        log("完成")
    except Exception:
        db.rollback()
        print(f"[seed] 失败阶段：{current_stage}", file=sys.stderr, flush=True)
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
