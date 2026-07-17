"""Create repeatable local development data for TalentFlow."""

from __future__ import annotations

import json
import os
import sys
import traceback
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit, urlunsplit

ROOT_DIR = Path(__file__).resolve().parents[1]
BACKEND_DIR = ROOT_DIR / "backend"
RECRUITMENT_MANIFEST = ROOT_DIR / "data" / "policies" / "recruitment" / "manifest.json"
sys.path.insert(0, str(ROOT_DIR))
sys.path.insert(0, str(BACKEND_DIR))
os.chdir(BACKEND_DIR)

from passlib.hash import bcrypt
from sqlalchemy import select, text
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import Base, SessionLocal
from app.modules import model_registry  # noqa: F401
from app.modules.attendance.models import AttendanceRecord, WorkCalendar
from app.modules.audit.models import AuditLog
from app.modules.auth.models import User
from app.modules.auth.permissions import ROLE_DEFAULT_PERMISSIONS
from app.modules.employee.models import Employee, LeaveBalance
from app.modules.interview.models import Interview, Interviewer, InterviewSlot, MeetingRoom
from app.modules.payroll.models import PayrollLineItem, PayrollPeriod, PayrollReviewRecord, SalaryRecord
from app.modules.policy.models import PolicyDocument
from app.modules.recruitment.models import Candidate, CandidateApplication, CandidatePipelineRecord, Job
from scripts.interview_availability_backfill import backfill_candidate_availability

EXPECTED_JOB_CODES = {"JOB-AGENT-001", "JOB-DATA-001", "JOB-AI-PLATFORM-001"}
POLICY_SEED_PATH = ROOT_DIR / "data" / "seed" / "policy_documents.json"
OFFICIAL_POLICY_SOURCE_HOSTS = {"flk.npc.gov.cn", "xzfg.moj.gov.cn", "www.mohrss.gov.cn"}
JOB_IDS = {
    "JOB-AGENT-001": 1,
    "JOB-DATA-001": 2,
    "JOB-AI-PLATFORM-001": 3,
}
JOB_DESCRIPTIONS = {
    "JOB-AGENT-001": "负责企业级 Agent、RAG、工具调用、状态持久化和可审计工作流开发。",
    "JOB-DATA-001": "负责批流数据处理、数据仓库、数据质量和企业可信数据底座建设。",
    "JOB-AI-PLATFORM-001": "负责模型网关、推理服务、Embedding、监控、限流和故障降级。",
}

CLEAR_ORDER = [
    "agent_tool_calls",
    "agent_events",
    "agent_run_nodes",
    "agent_runs",
    "payroll_line_items",
    "audit_logs",
    "notifications",
    "leave_requests",
    "interviews",
    "interview_slots",
    "candidate_pipeline_records",
    "payroll_review_records",
    "payroll_adjustments",
    "payroll_rules",
    "salary_records",
    "payroll_periods",
    "interviewers",
    "meeting_rooms",
    "candidate_applications",
    "candidates",
    "jobs",
    "attendance_records",
    "work_calendars",
    "leave_balances",
    "policy_documents",
    "employees",
    "users",
]


def log(stage: str) -> None:
    print(f"[seed] {stage}", flush=True)


def masked_database_url(url: str) -> str:
    parsed = urlsplit(url)
    port = f":{parsed.port}" if parsed.port else ""
    credentials = f"{parsed.username}:***@" if parsed.username else ""
    return urlunsplit((parsed.scheme, f"{credentials}{parsed.hostname or ''}{port}", parsed.path, "", ""))


def load_active_job_standards() -> dict[str, dict[str, Any]]:
    """Load the three database job definitions from the active RAG manifest."""

    payload = json.loads(RECRUITMENT_MANIFEST.read_text(encoding="utf-8"))
    documents = payload.get("documents")
    if not isinstance(documents, list):
        raise ValueError("招聘知识库 Manifest 缺少 documents 数组。")

    standards: dict[str, dict[str, Any]] = {}
    for document in documents:
        if not isinstance(document, dict):
            continue
        if document.get("is_active") is not True or document.get("document_type") != "JOB_STANDARD":
            continue
        job_code = document.get("job_code")
        if not isinstance(job_code, str) or not job_code.strip():
            raise ValueError("活跃岗位标准缺少 job_code。")
        if job_code in standards:
            raise ValueError(f"招聘知识库 Manifest 存在重复岗位：{job_code}")
        attributes = document.get("attributes")
        if not isinstance(attributes, dict):
            raise ValueError(f"岗位标准 {job_code} 缺少 attributes。")
        for field_name in ("required_skills", "preferred_skills"):
            value = attributes.get(field_name)
            if not isinstance(value, list) or not all(isinstance(item, str) and item.strip() for item in value):
                raise ValueError(f"岗位标准 {job_code} 的 {field_name} 无效。")
        if not isinstance(attributes.get("min_experience_months"), int):
            raise ValueError(f"岗位标准 {job_code} 的 min_experience_months 无效。")
        if not isinstance(document.get("title"), str) or not isinstance(document.get("department"), str):
            raise ValueError(f"岗位标准 {job_code} 缺少 title 或 department。")
        standards[job_code] = document

    if set(standards) != EXPECTED_JOB_CODES:
        missing = sorted(EXPECTED_JOB_CODES - set(standards))
        unexpected = sorted(set(standards) - EXPECTED_JOB_CODES)
        raise ValueError(f"活跃岗位标准必须恰好为三个；缺少={missing}，多余={unexpected}。")
    return standards


def load_policy_documents() -> list[dict[str, Any]]:
    """Load and validate public policy metadata from official government sources."""

    payload = json.loads(POLICY_SEED_PATH.read_text(encoding="utf-8"))
    if not isinstance(payload, list) or not payload:
        raise ValueError("政策种子数据必须是非空数组。")

    required_fields = {"document_code", "title", "category", "source_path", "version", "metadata_json"}
    document_codes: set[str] = set()
    documents: list[dict[str, Any]] = []
    for index, item in enumerate(payload, 1):
        if not isinstance(item, dict):
            raise ValueError(f"第 {index} 条政策种子数据不是对象。")
        missing_fields = sorted(required_fields - item.keys())
        if missing_fields:
            raise ValueError(f"第 {index} 条政策种子数据缺少字段：{missing_fields}")

        document_code = item["document_code"]
        if not isinstance(document_code, str) or not document_code.strip():
            raise ValueError(f"第 {index} 条政策种子数据的 document_code 无效。")
        if document_code in document_codes:
            raise ValueError(f"政策种子数据存在重复 document_code：{document_code}")
        document_codes.add(document_code)

        for field_name in ("title", "category", "source_path", "version"):
            value = item[field_name]
            if not isinstance(value, str) or not value.strip():
                raise ValueError(f"政策 {document_code} 的 {field_name} 无效。")

        source = urlsplit(item["source_path"])
        if source.scheme != "https" or source.hostname not in OFFICIAL_POLICY_SOURCE_HOSTS:
            raise ValueError(f"政策 {document_code} 必须使用允许的政府官方 HTTPS 来源。")

        metadata = item["metadata_json"]
        if not isinstance(metadata, dict) or not isinstance(metadata.get("summary"), str) or not metadata["summary"].strip():
            raise ValueError(f"政策 {document_code} 缺少有效摘要。")
        if metadata.get("status") != "现行有效":
            raise ValueError(f"政策 {document_code} 必须明确标记为现行有效。")

        documents.append({
            "document_code": document_code.strip(),
            "title": item["title"].strip(),
            "category": item["category"].strip(),
            "source_path": item["source_path"].strip(),
            "version": item["version"].strip(),
            "is_active": item.get("is_active", True) is True,
            "metadata_json": metadata,
        })
    return documents


def upsert_policy_documents(db: Session) -> int:
    """Insert or update official policy metadata without deleting unrelated data."""

    policies = load_policy_documents()
    codes = [policy["document_code"] for policy in policies]
    existing = {
        policy.document_code: policy
        for policy in db.scalars(select(PolicyDocument).where(PolicyDocument.document_code.in_(codes)))
    }
    for values in policies:
        document = existing.get(values["document_code"])
        if document is None:
            db.add(PolicyDocument(**values))
            continue
        for field_name, value in values.items():
            setattr(document, field_name, value)
    db.commit()
    return len(policies)


def clear_existing_data(db: Session) -> None:
    for table_name in CLEAR_ORDER:
        table = Base.metadata.tables.get(table_name)
        if table is not None:
            db.execute(table.delete())
    db.commit()


def add_users(db: Session, password_hash: str) -> None:
    db.add_all([
        User(id=1, username="zhangwei", password_hash=password_hash, role="EMPLOYEE", permissions=ROLE_DEFAULT_PERMISSIONS["EMPLOYEE"]),
        User(id=2, username="liming", password_hash=password_hash, role="DEPARTMENT_MANAGER", permissions=ROLE_DEFAULT_PERMISSIONS["DEPARTMENT_MANAGER"]),
        User(id=3, username="linyuqing", password_hash=password_hash, role="HR_SPECIALIST", permissions=ROLE_DEFAULT_PERMISSIONS["HR_SPECIALIST"]),
        User(id=4, username="wangqiang", password_hash=password_hash, role="PAYROLL_ADMIN", permissions=ROLE_DEFAULT_PERMISSIONS["PAYROLL_ADMIN"]),
    ])
    db.commit()


def add_employees(db: Session, today: date) -> None:
    db.add_all([
        Employee(
            id=2,
            user_id=2,
            employee_no="EMP002",
            full_name="李明",
            department="智能应用研发部",
            job_title="智能应用研发部经理",
            email="liming@example.test",
            phone="13900000002",
            hire_date=today - timedelta(days=1200),
        ),
        Employee(
            id=3,
            user_id=3,
            employee_no="EMP003",
            full_name="林雨晴",
            department="人力资源部",
            job_title="HR 专员",
            email="linyuqing@example.test",
            phone="13900000003",
            hire_date=today - timedelta(days=700),
        ),
        Employee(
            id=4,
            user_id=4,
            employee_no="EMP004",
            full_name="王强",
            department="财务部",
            job_title="薪酬管理员",
            email="wangqiang@example.test",
            phone="13900000004",
            hire_date=today - timedelta(days=900),
        ),
        Employee(
            id=5,
            user_id=None,
            employee_no="EMP005",
            full_name="周明澈",
            department="数据平台研发部",
            job_title="数据平台研发部经理",
            email="zhoumingche@example.test",
            phone="13900000005",
            hire_date=today - timedelta(days=1100),
        ),
        Employee(
            id=6,
            user_id=None,
            employee_no="EMP006",
            full_name="何远航",
            department="AI 基础设施部",
            job_title="AI 基础设施部经理",
            email="heyuanhang@example.test",
            phone="13900000006",
            hire_date=today - timedelta(days=1000),
        ),
    ])
    db.flush()
    db.add(Employee(
        id=1,
        user_id=1,
        employee_no="EMP001",
        full_name="张伟",
        department="智能应用研发部",
        job_title="Agent 应用开发工程师",
        manager_employee_id=2,
        email="zhangwei@example.test",
        phone="13900000001",
        hire_date=today - timedelta(days=500),
    ))
    db.add_all([
        LeaveBalance(
            id=employee_id,
            employee_id=employee_id,
            leave_type="ANNUAL",
            year=today.year,
            total_days=days,
            used_days=0,
        )
        for employee_id, days in [(1, 10), (2, 15), (3, 10), (4, 10), (5, 15), (6, 15)]
    ])
    db.commit()


def add_recruitment(db: Session, today: date) -> None:
    standards = load_active_job_standards()
    log("写入招聘岗位")
    jobs: list[Job] = []
    for job_code, job_id in JOB_IDS.items():
        standard = standards[job_code]
        attributes = standard["attributes"]
        title = standard["title"].removesuffix("岗位标准").strip()
        jobs.append(Job(
            id=job_id,
            job_code=job_code,
            title=title,
            department=standard["department"],
            description=JOB_DESCRIPTIONS[job_code],
            required_skills=list(attributes["required_skills"]),
            preferred_skills=list(attributes["preferred_skills"]),
            min_experience_months=attributes["min_experience_months"],
            location="武汉",
            employment_type="FULL_TIME",
            status="OPEN",
            owner_user_id=3,
        ))
    db.add_all(jobs)

    candidate_rows = [
        {
            "id": 1,
            "candidate_no": "CAN-AG-001",
            "full_name": "陈晨",
            "email": "chenchen@example.test",
            "phone": "13800000001",
            "skills": ["Python", "FastAPI", "REST API", "LLM API", "Agent", "RAG", "Tool Calling", "PostgreSQL", "Docker", "ChromaDB"],
            "experience_months": 30,
            "available_from": today + timedelta(days=14),
            "resume_text": (
                "陈晨具有 30 个月 Python 智能应用开发经历，主要使用 FastAPI、PostgreSQL 和 Docker 交付企业应用。"
                "能够说明 REST API、模型接口和工具调用之间的权限边界。\n\n"
                "在企业招聘多 Agent 决策平台中，负责 Agent 工作流、RAG 检索、SSE 事件流和 PostgreSQL Run 持久化。"
                "项目记录了节点状态、知识来源与工具执行摘要，并在模型异常时进入可审计的自动回退流程。\n\n"
                "候选人能够完整说明本人负责范围、接口契约和故障恢复方式，项目证据与岗位要求匹配度较高。"
            ),
            "profile_json": {
                "education": ["软件工程本科"],
                "projects": ["企业招聘多 Agent 决策平台"],
                "project_roles": ["负责 Agent 工作流、RAG 检索、SSE 事件流和 PostgreSQL Run 持久化"],
                "project_technologies": ["Python", "FastAPI", "LangGraph", "ChromaDB", "PostgreSQL", "Docker"],
                "measurable_achievements": ["将模型异常后的恢复方式由人工处理改为自动回退", "完成可追踪的多 Agent 节点状态与来源记录"],
                "certificates": ["软件设计师资格证书"],
            },
        },
        {
            "id": 2,
            "candidate_no": "CAN-AG-002",
            "full_name": "吴桐",
            "email": "wutong@example.test",
            "phone": "13800000002",
            "skills": ["Python", "FastAPI", "LLM API", "PostgreSQL", "基础 RAG"],
            "experience_months": 14,
            "available_from": today + timedelta(days=21),
            "resume_text": (
                "吴桐具有 14 个月 Python 与 FastAPI 项目经历，能够完成基础接口开发、模型调用和 PostgreSQL 数据读写。"
                "目前的 Agent 与 RAG 经验主要来自课程实践。\n\n"
                "在课程知识库问答系统中，完成模型调用、文档切片和基础向量检索，能够展示完整问答流程。"
                "材料中尚未体现复杂 Agent 编排、生产部署、模型回退和 RAG 评测。\n\n"
                "候选人具备继续培养基础，但需要通过面试确认状态管理、异常处理和可审计工程能力。"
            ),
            "profile_json": {
                "education": ["计算机应用技术本科"],
                "projects": ["课程知识库问答系统"],
                "project_roles": ["完成模型调用、文档切片和基础向量检索"],
                "project_technologies": ["Python", "FastAPI", "PostgreSQL"],
                "measurable_achievements": [],
                "certificates": [],
            },
        },
        {
            "id": 3,
            "candidate_no": "CAN-DATA-001",
            "full_name": "周晓",
            "email": "zhouxiao@example.test",
            "phone": "13800000003",
            "skills": ["Python", "SQL", "Spark", "Flink", "Kafka", "ETL", "ClickHouse", "数据仓库"],
            "experience_months": 36,
            "available_from": today + timedelta(days=10),
            "resume_text": (
                "周晓具有 36 个月数据平台开发经历，熟悉 Python、SQL、Spark、Flink、Kafka 和 ClickHouse。"
                "能够从数据接入、实时计算到指标服务说明完整链路。\n\n"
                "在企业实时经营数据平台中，负责 Kafka 数据接入、Flink 实时任务和 ClickHouse 指标服务。"
                "实际处理过重复消费、Checkpoint 失败和 Spark 数据倾斜，并能说明定位与恢复过程。\n\n"
                "项目职责、技术栈和故障证据较完整，适合进入结构化技术面试。"
            ),
            "profile_json": {
                "education": ["数据科学与大数据技术本科"],
                "projects": ["企业实时经营数据平台"],
                "project_roles": ["负责 Kafka 数据接入、Flink 实时任务和 ClickHouse 指标服务"],
                "project_technologies": ["Python", "SQL", "Spark", "Flink", "Kafka", "ClickHouse"],
                "measurable_achievements": ["完成重复消费幂等治理", "处理 Checkpoint 失败和 Spark 数据倾斜"],
                "certificates": ["数据工程专项课程结业证书"],
            },
        },
        {
            "id": 4,
            "candidate_no": "CAN-DATA-002",
            "full_name": "李然",
            "email": "liran@example.test",
            "phone": "13800000004",
            "skills": ["SQL", "Spark", "Hive", "ETL", "数据仓库", "Linux"],
            "experience_months": 20,
            "available_from": today + timedelta(days=18),
            "resume_text": (
                "李然具有 20 个月离线数据处理经历，日常使用 SQL、Spark、Hive 和 Linux 完成 ETL 开发。"
                "对数据仓库分层和定时任务有实际项目经验。\n\n"
                "在离线销售数据仓库项目中，负责数据清洗、数仓分层和定时任务维护。"
                "现有材料没有展示 Kafka、Flink、实时处理或完整数据质量体系。\n\n"
                "候选人与离线数仓方向部分匹配，需进一步确认实时链路和质量治理能力。"
            ),
            "profile_json": {
                "education": ["信息管理本科"],
                "projects": ["离线销售数据仓库"],
                "project_roles": ["负责数据清洗、数仓分层和定时任务"],
                "project_technologies": ["SQL", "Spark", "Hive", "Linux"],
                "measurable_achievements": [],
                "certificates": [],
            },
        },
        {
            "id": 5,
            "candidate_no": "CAN-AIP-001",
            "full_name": "何川",
            "email": "hechuan@example.test",
            "phone": "13800000005",
            "skills": ["Python", "Linux", "Docker", "Kubernetes", "模型 API", "模型网关", "Prometheus", "OpenTelemetry", "故障排查"],
            "experience_months": 34,
            "available_from": today + timedelta(days=12),
            "resume_text": (
                "何川具有 34 个月模型平台和基础设施开发经历，熟悉 Python、Linux、Docker、Kubernetes 与模型 API。"
                "能够说明模型网关、监控和故障处理的协作边界。\n\n"
                "在企业多模型统一接入平台中，负责模型网关、限流、重试、熔断、链路追踪和版本切换。"
                "项目处理过模型接口不兼容、429、5xx 和超时降级问题，并保留了故障定位记录。\n\n"
                "候选人具备较完整的平台交付与故障处理证据，和岗位核心职责高度匹配。"
            ),
            "profile_json": {
                "education": ["计算机科学与技术本科"],
                "projects": ["企业多模型统一接入平台"],
                "project_roles": ["负责模型网关、限流、重试、熔断、链路追踪和版本切换"],
                "project_technologies": ["Python", "Docker", "Kubernetes", "Prometheus", "OpenTelemetry"],
                "measurable_achievements": ["处理模型接口不兼容与 429、5xx 错误", "建立超时降级与模型版本切换流程"],
                "certificates": ["云原生应用开发课程结业证书"],
            },
        },
        {
            "id": 6,
            "candidate_no": "CAN-AIP-002",
            "full_name": "郑凯",
            "email": "zhengkai@example.test",
            "phone": "13800000006",
            "skills": ["Python", "Linux", "Docker", "HTTP", "Prometheus", "Grafana"],
            "experience_months": 20,
            "available_from": today + timedelta(days=20),
            "resume_text": (
                "郑凯具有 20 个月后端服务部署与监控经历，能够使用 Python、Linux 和 Docker 维护常规 HTTP 服务。"
                "熟悉 Prometheus 与 Grafana 的基础指标展示。\n\n"
                "在后端服务部署与监控平台中，负责容器部署和基础服务监控，能够处理常见进程和网络问题。"
                "材料中缺少模型网关、推理服务、Embedding 和模型版本管理经验。\n\n"
                "候选人具备基础平台能力，但模型服务方向的证据仍需通过面试补充。"
            ),
            "profile_json": {
                "education": ["网络工程本科"],
                "projects": ["后端服务部署与监控平台"],
                "project_roles": ["负责容器部署和基础服务监控"],
                "project_technologies": ["Python", "Linux", "Docker", "Prometheus", "Grafana"],
                "measurable_achievements": [],
                "certificates": [],
            },
        },
    ]
    log("写入候选人")
    db.add_all([
        Candidate(
            **row,
            resume_file_path=None,
            source="SEED",
        )
        for row in candidate_rows
    ])
    db.flush()

    application_rows = [
        (1, 1, 1, "INTERVIEW_PENDING", "91", {"skill": 94, "experience": 90, "project": 95, "education": 84, "risk": 92, "match_score": 93, "overall_score": 91}),
        (2, 2, 1, "AI_SCREENED", "76", {"skill": 78, "experience": 72, "project": 75, "education": 80, "risk": 73, "match_score": 76, "overall_score": 76}),
        (3, 3, 2, "INTERVIEW_PENDING", "90", {"skill": 93, "experience": 91, "project": 92, "education": 82, "risk": 89, "match_score": 92, "overall_score": 90}),
        (4, 4, 2, "AI_SCREENED", "77", {"skill": 80, "experience": 75, "project": 77, "education": 81, "risk": 72, "match_score": 76, "overall_score": 77}),
        (5, 5, 3, "INTERVIEW_PENDING", "92", {"skill": 95, "experience": 92, "project": 94, "education": 83, "risk": 93, "match_score": 94, "overall_score": 92}),
        (6, 6, 3, "AI_SCREENED", "75", {"skill": 77, "experience": 73, "project": 72, "education": 80, "risk": 74, "match_score": 74, "overall_score": 75}),
    ]
    weights = {"skill": 0.3, "experience": 0.2, "project": 0.25, "education": 0.1, "risk": 0.15}
    scored_at = datetime.now().astimezone()
    log("写入候选人申请")
    db.add_all([
        CandidateApplication(
            id=application_id,
            candidate_id=candidate_id,
            job_id=job_id,
            current_stage=stage,
            score_total=Decimal(score),
            score_breakdown=breakdown,
            weights_snapshot=weights,
            scored_at=scored_at,
        )
        for application_id, candidate_id, job_id, stage, score, breakdown in application_rows
    ])
    db.flush()
    db.add_all([
        CandidatePipelineRecord(
            id=application_id,
            application_id=application_id,
            from_stage=None,
            to_stage=stage,
            note="初始化招聘阶段",
            changed_by_user_id=3,
        )
        for application_id, _candidate_id, _job_id, stage, _score, _breakdown in application_rows
    ])
    db.commit()
    sync_recruitment_sequences(db)


def sync_recruitment_sequences(db: Session) -> None:
    """Keep PostgreSQL identity sequences aligned after fixed-ID demo seeding."""

    for table_name in ("candidates", "candidate_applications", "candidate_pipeline_records"):
        db.execute(text(
            f"SELECT setval(pg_get_serial_sequence('{table_name}', 'id'), "
            f"COALESCE(MAX(id), 1), MAX(id) IS NOT NULL) FROM {table_name}"
        ))
    db.commit()


def _next_workday(day: date) -> date:
    candidate = day + timedelta(days=1)
    while candidate.weekday() >= 5:
        candidate += timedelta(days=1)
    return candidate


def add_interviews(db: Session, now: datetime) -> None:
    interview_day = _next_workday(now.date())
    start = datetime.combine(interview_day, time(14), tzinfo=now.tzinfo)
    end = start + timedelta(hours=1)
    log("写入面试官")
    db.add_all([
        Interviewer(id=1, employee_id=2, specialties=["Python", "Agent", "RAG", "系统设计"], max_interviews_per_day=4),
        Interviewer(id=2, employee_id=5, specialties=["Spark", "Flink", "Kafka", "数据仓库"], max_interviews_per_day=4),
        Interviewer(id=3, employee_id=6, specialties=["模型网关", "Docker", "Kubernetes", "服务监控"], max_interviews_per_day=4),
        Interviewer(id=4, employee_id=3, specialties=["沟通表达", "项目真实性", "招聘合规"], max_interviews_per_day=5),
    ])
    log("写入会议室")
    db.add_all([
        MeetingRoom(id=1, room_code="WH-A101", name="云杉会议室", location="武汉总部 A 座 1 层", capacity=6),
        MeetingRoom(id=2, room_code="WH-B201", name="星河会议室", location="武汉总部 B 座 2 层", capacity=8),
    ])
    db.flush()
    log("写入少量面试数据")
    db.add_all([
        InterviewSlot(resource_type="INTERVIEWER", interviewer_id=2, start_at=start, end_at=end, note="周明澈可用时段"),
        InterviewSlot(resource_type="ROOM", meeting_room_id=1, start_at=start, end_at=end, note="云杉会议室可用时段"),
        Interview(
            id=1,
            application_id=3,
            interviewer_id=2,
            meeting_room_id=1,
            start_at=start,
            end_at=end,
            status="SCHEDULED",
            conflict_explanation={"note": "已确认候选人、面试官和会议室可用"},
            created_by_user_id=3,
        ),
    ])
    db.flush()

    shared_interviewer_id = db.scalar(
        select(Interviewer.id).where(Interviewer.is_active.is_(True)).order_by(Interviewer.id)
    )
    shared_room_id = db.scalar(
        select(MeetingRoom.id).where(MeetingRoom.is_active.is_(True)).order_by(MeetingRoom.id)
    )
    if shared_interviewer_id is None or shared_room_id is None:
        raise RuntimeError("演示数据缺少启用的面试官或会议室。")

    shared_windows: list[tuple[datetime, datetime]] = []
    shared_day = now.date()
    for _ in range(4):
        shared_day = _next_workday(shared_day)
        shared_start = datetime.combine(shared_day, time(9), tzinfo=now.tzinfo)
        shared_windows.append((shared_start, shared_start + timedelta(hours=3)))
    db.add_all([
        InterviewSlot(
            resource_type="INTERVIEWER",
            interviewer_id=shared_interviewer_id,
            start_at=window_start,
            end_at=window_end,
            note="demo shared interviewer availability",
        )
        for window_start, window_end in shared_windows
    ] + [
        InterviewSlot(
            resource_type="ROOM",
            meeting_room_id=shared_room_id,
            start_at=window_start,
            end_at=window_end,
            note="demo shared room availability",
        )
        for window_start, window_end in shared_windows
    ])
    db.flush()

    availability_stats = backfill_candidate_availability(db, now=now)
    log(
        f"候选人可用时间：新增候选人 {availability_stats.backfilled_candidates}，"
        f"新增时段 {availability_stats.created_slots}，跳过候选人 {availability_stats.skipped_candidates}"
    )
    db.commit()


def add_attendance(db: Session, today: date, now: datetime) -> None:
    log("写入工作日历")
    for offset in range(-7, 8):
        day = today + timedelta(days=offset)
        workday = day.weekday() < 5 or day == today
        db.add(WorkCalendar(
            calendar_date=day,
            is_workday=workday,
            standard_check_in_time=time(9),
            standard_check_out_time=time(18),
            late_grace_minutes=10,
            holiday_name=None if workday else "周末",
        ))
    history_day = today - timedelta(days=1)
    log("写入考勤记录")
    db.add(AttendanceRecord(
        employee_id=2,
        attendance_date=history_day,
        check_in_at=now.replace(year=history_day.year, month=history_day.month, day=history_day.day, hour=8, minute=55),
        check_out_at=now.replace(year=history_day.year, month=history_day.month, day=history_day.day, hour=18, minute=5),
        status="NORMAL",
        source="SEED",
    ))
    db.commit()


def add_payroll(db: Session, today: date) -> None:
    log("写入薪资记录")
    amounts = ["25000", "35000", "18000", "20000"]
    salaries = [
        SalaryRecord(
            id=index,
            employee_id=index,
            base_salary=Decimal(amount),
            effective_from=date(today.year, 1, 1),
            created_by_user_id=4,
        )
        for index, amount in enumerate(amounts, 1)
    ]
    period_start = today.replace(day=1)
    next_month = (period_start.replace(day=28) + timedelta(days=4)).replace(day=1)
    db.add_all([*salaries, PayrollPeriod(
        id=1,
        period_code=period_start.strftime("%Y-%m"),
        start_date=period_start,
        end_date=next_month - timedelta(days=1),
        standard_work_days=Decimal("22"),
        status="OPEN",
    )])
    db.flush()
    reviews = [
        PayrollReviewRecord(
            id=index,
            employee_id=index,
            payroll_period_id=1,
            salary_record_id=index,
            status="PENDING_HR_CONFIRMATION",
            base_salary_snapshot=Decimal(amount),
            standard_work_days_snapshot=Decimal("22"),
            calculation_snapshot={"source": "seed"},
            total_earnings=Decimal(amount),
            total_deductions=Decimal("0"),
            net_salary_preview=Decimal(amount),
            generated_by_user_id=4,
        )
        for index, amount in enumerate(amounts, 1)
    ]
    db.add_all(reviews)
    db.flush()
    db.add_all([
        PayrollLineItem(
            payroll_review_record_id=item.id,
            item_type="EARNING",
            item_name="基本工资",
            amount=item.base_salary_snapshot,
            source_type="RULE",
            source_reference_json={"salary_record_id": item.salary_record_id},
            calculation_detail_json={"formula": "月度基本工资"},
        )
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
        AuditLog(
            actor_user_id=user_id,
            actor_role=role,
            target_employee_id=target_id,
            action="QUERY_SALARY",
            resource_type="SALARY",
            resource_id=target_id,
            requested_fields=["base_salary", "currency", "effective_from", "effective_to"],
            result=result,
            reason=reason,
            trace_id=f"seed-{index:03d}",
        )
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
            ("写入官方政策文档", lambda: upsert_policy_documents(db)),
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


def seed_policy_documents() -> None:
    """Upsert only official policy documents, preserving all other database tables."""

    settings = get_settings()
    print(f"[seed-policy] DATABASE_URL={masked_database_url(settings.database_url)}", flush=True)
    db = SessionLocal()
    try:
        log("写入官方政策文档")
        count = upsert_policy_documents(db)
        print(f"[seed-policy] 完成，共写入或更新 {count} 条政策。", flush=True)
    except Exception:
        db.rollback()
        print("[seed-policy] 写入失败", file=sys.stderr, flush=True)
        traceback.print_exc()
        raise
    finally:
        db.close()


if __name__ == "__main__":
    seed_data()
