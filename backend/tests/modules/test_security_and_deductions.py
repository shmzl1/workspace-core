import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///test.db"

import pytest
from datetime import date, datetime, time, timedelta
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal

from app.modules.auth.models import User
from app.modules.auth.permissions import ROLE_DEFAULT_PERMISSIONS
from app.modules.employee.models import Employee, LeaveBalance
from app.modules.payroll.models import SalaryRecord, PayrollPeriod, PayrollReviewRecord, PayrollLineItem
from app.modules.attendance.models import AttendanceRecord, WorkCalendar
from app.modules.audit.models import AuditLog

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB
from app.core.security import create_access_token

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"

client = TestClient(app)

@pytest.fixture(scope="module", autouse=True)
def setup_test_db():
    db = SessionLocal()
    try:
        if "sqlite" in str(engine.url):
            needed_tables = {
                "users", "employees", "leave_balances", "salary_records", 
                "attendance_records", "audit_logs", "work_calendars",
                "payroll_periods", "payroll_review_records", "payroll_line_items"
            }
            for table_name in list(Base.metadata.tables.keys()):
                if table_name not in needed_tables:
                    Base.metadata.remove(Base.metadata.tables[table_name])
            
            from sqlalchemy import text
            for table in Base.metadata.tables.values():
                for column in table.columns:
                    if column.server_default is not None:
                        arg_str = str(column.server_default.arg)
                        if "::jsonb" in arg_str:
                            arg_str = arg_str.replace("::jsonb", "")
                        if "now()" in arg_str:
                            arg_str = arg_str.replace("now()", "CURRENT_TIMESTAMP")
                        column.server_default.arg = text(arg_str)
            Base.metadata.drop_all(bind=engine)
            Base.metadata.create_all(bind=engine)

            # Seed users
            user1 = User(id=1, username="zhangwei", password_hash="hash", role="EMPLOYEE", permissions=ROLE_DEFAULT_PERMISSIONS["EMPLOYEE"], is_active=True)
            user2 = User(id=2, username="liming", password_hash="hash", role="DEPARTMENT_MANAGER", permissions=ROLE_DEFAULT_PERMISSIONS["DEPARTMENT_MANAGER"], is_active=True)
            user3 = User(id=3, username="linyuqing", password_hash="hash", role="HR_SPECIALIST", permissions=["payroll.review.read", "payroll.masked.read", "employee.self.read", "policy.read", "audit.read", "agent.hr.use"], is_active=True)
            user4 = User(id=4, username="wangqiang", password_hash="hash", role="PAYROLL_ADMIN", permissions=ROLE_DEFAULT_PERMISSIONS["PAYROLL_ADMIN"], is_active=True)
            db.add_all([user1, user2, user3, user4])
            db.commit()
            
            # Seed employees
            emp1 = Employee(id=1, user_id=1, employee_no="EMP001", full_name="张伟", department="研发部", job_title="高级工程师", manager_employee_id=2, employment_status="ACTIVE")
            emp2 = Employee(id=2, user_id=2, employee_no="EMP002", full_name="李明", department="研发部", job_title="研发主管", employment_status="ACTIVE")
            emp3 = Employee(id=3, user_id=3, employee_no="EMP003", full_name="林雨晴", department="人事部", job_title="HR专员", employment_status="ACTIVE")
            emp4 = Employee(id=4, user_id=4, employee_no="EMP004", full_name="王强", department="财务部", job_title="薪酬管理员", employment_status="ACTIVE")
            db.add_all([emp1, emp2, emp3, emp4])
            db.commit()
            
            # Seed salary records
            sal1 = SalaryRecord(id=1, employee_id=1, base_salary=Decimal("25000.00"), currency="CNY", effective_from=date(2026, 1, 1))
            sal2 = SalaryRecord(id=2, employee_id=2, base_salary=Decimal("35000.00"), currency="CNY", effective_from=date(2026, 1, 1))
            db.add_all([sal1, sal2])
            db.commit()
            
            # Seed leave balance
            leave1 = LeaveBalance(id=1, employee_id=1, leave_type="ANNUAL", year=2026, total_days=Decimal("15.00"), used_days=Decimal("3.00"))
            db.add(leave1)
            db.commit()

            # Seed calendar
            for d in range(1, 32):
                cal = WorkCalendar(
                    calendar_date=date(2026, 7, d),
                    is_workday=True,
                    standard_check_in_time=time(9, 0),
                    standard_check_out_time=time(18, 0),
                    late_grace_minutes=10,
                )
                db.add(cal)
            db.commit()

            # Seed attendance records for zhangwei (employee_id=1) in July 2026
            # 1. Late: July 1
            att1 = AttendanceRecord(employee_id=1, attendance_date=date(2026, 7, 1), status="LATE", late_minutes=15, source="WEB")
            # 2. Early leave: July 2
            att2 = AttendanceRecord(employee_id=1, attendance_date=date(2026, 7, 2), status="EARLY_LEAVE", early_leave_minutes=20, source="WEB")
            # 3. Absent: July 3
            att3 = AttendanceRecord(employee_id=1, attendance_date=date(2026, 7, 3), status="ABSENT", source="WEB")
            # 4. Unpaid leave: July 6
            att4 = AttendanceRecord(employee_id=1, attendance_date=date(2026, 7, 6), status="UNPAID_LEAVE", source="WEB")
            # 5. Normal check-in: July 7
            att5 = AttendanceRecord(employee_id=1, attendance_date=date(2026, 7, 7), status="NORMAL", source="WEB")
            db.add_all([att1, att2, att3, att4, att5])
            db.commit()

            # Seed payroll period for July 2026
            period = PayrollPeriod(id=1, period_code="2026-07", start_date=date(2026, 7, 1), end_date=date(2026, 7, 31), standard_work_days=Decimal("22.00"), status="OPEN")
            db.add(period)
            db.commit()

            # Seed payroll review record for zhangwei
            review1 = PayrollReviewRecord(
                id=1, employee_id=1, payroll_period_id=1, salary_record_id=1,
                status="DRAFT", base_salary_snapshot=Decimal("22000.00"),
                standard_work_days_snapshot=Decimal("22.00"), total_earnings=Decimal("22000.00"),
                total_deductions=Decimal("0.00"), net_salary_preview=Decimal("22000.00"),
            )
            db.add(review1)
            db.commit()

            # Seed basic earning line item
            earning_item = PayrollLineItem(
                payroll_review_record_id=1, item_type="EARNING", item_name="基本工资",
                amount=Decimal("22000.00"), source_type="RULE"
            )
            db.add(earning_item)
            db.commit()
    finally:
        db.close()
    yield


def get_auth_headers(user_id: int, username: str) -> dict[str, str]:
    token = create_access_token({"user_id": user_id, "sub": username}, timedelta(hours=1))
    return {"Authorization": f"Bearer {token}"}


def test_get_monthly_attendance_summary():
    headers_self = get_auth_headers(1, "zhangwei")
    headers_manager = get_auth_headers(2, "liming")
    headers_other = get_auth_headers(3, "linyuqing")

    # 1. zhangwei queries own summary
    response = client.get("/api/v1/attendance/monthly?year=2026&month=7", headers=headers_self)
    assert response.status_code == 200
    data = response.json()["data"]
    assert data["employee_id"] == 1
    assert data["late_count"] == 1
    assert data["early_leave_count"] == 1
    assert data["absent_count"] == 1
    assert data["unpaid_leave_count"] == 1
    assert float(data["remaining_days"]) == 12.0

    # 2. zhangwei queries employee 2 (forbidden)
    response = client.get("/api/v1/attendance/monthly?year=2026&month=7&employee_id=2", headers=headers_self)
    assert response.status_code == 403

    # 3. liming (manager) queries employee 1 (allowed because employee 1 is in liming's department/subordinate)
    response = client.get("/api/v1/attendance/monthly?year=2026&month=7&employee_id=1", headers=headers_manager)
    assert response.status_code == 200


def test_pre_audit_calculations_and_data_isolation():
    headers_admin = get_auth_headers(4, "wangqiang")

    # Call pre-audit endpoint to calculate
    response = client.post(
        "/api/v1/payroll-review/pre-audit",
        json={"target_record_ids": [1], "include_line_items": True},
        headers=headers_admin
    )
    assert response.status_code == 200

    # Verify that the database contains the calculated line items (without modifying attendance)
    db = SessionLocal()
    try:
        review = db.get(PayrollReviewRecord, 1)
        # base_salary_snapshot = 22000.00, standard_work_days_snapshot = 22.00 -> daily_rate = 1000.00
        # Deductions should be:
        # Late count = 1 -> 50.00
        # Early leave = 1 -> 50.00
        # Absent = 1 -> 1000.00
        # Unpaid leave = 1 -> 1000.00
        # Total Deductions = 50 + 50 + 1000 + 1000 = 2100.00
        # Net salary = 22000.00 - 2100.00 = 19900.00
        assert float(review.total_deductions) == 2100.00
        assert float(review.net_salary_preview) == 19900.00

        # Check line items
        items = db.query(PayrollLineItem).filter(PayrollLineItem.payroll_review_record_id == 1).all()
        item_names = [it.item_name for it in items]
        assert any("迟到扣款" in name for name in item_names)
        assert any("早退扣款" in name for name in item_names)
        assert any("缺勤扣款" in name for name in item_names)
        assert any("无薪假扣款" in name for name in item_names)

        # Check that no write occurred on AttendanceRecord
        att_count = db.query(AttendanceRecord).count()
        assert att_count == 5  # No new record written
    finally:
        db.close()


def test_pre_audit_row_level_and_masking():
    # 1. zhangwei (EMPLOYEE) has no payroll.review.read permission -> should get 403 on records endpoint
    headers_self = get_auth_headers(1, "zhangwei")
    response = client.get("/api/v1/payroll-review/records", headers=headers_self)
    assert response.status_code == 403

    # 2. linyuqing (HR_SPECIALIST) has payroll.review.read and payroll.masked.read
    headers_hr = get_auth_headers(3, "linyuqing")
    response = client.get("/api/v1/payroll-review/records/1", headers=headers_hr)
    assert response.status_code == 200
    data = response.json()["data"]
    # Check masking: financial amounts should be 0.00
    assert float(data["base_salary_snapshot"]) == 0.00
    assert float(data["net_salary_preview"]) == 0.00

    # 3. wangqiang (PAYROLL_ADMIN) has full access
    headers_admin = get_auth_headers(4, "wangqiang")
    response = client.get("/api/v1/payroll-review/records/1", headers=headers_admin)
    assert response.status_code == 200
    data = response.json()["data"]
    # Check that they can view actual salary
    assert float(data["base_salary_snapshot"]) == 22000.00
    assert float(data["net_salary_preview"]) == 19900.00


def test_agent_tools_execution():
    from app.agents.tools.employee_service import (
        get_my_monthly_attendance_summary,
        get_my_annual_leave_balance,
        get_my_salary_details,
    )
    
    db = SessionLocal()
    try:
        # Test get_my_monthly_attendance_summary tool
        summary = get_my_monthly_attendance_summary(2026, 7, db, 1)
        assert summary["late_count"] == 1
        assert float(summary["remaining_days"]) == 12.0

        # Test get_my_annual_leave_balance tool
        leave = get_my_annual_leave_balance(2026, db, 1)
        assert float(leave["total_days"]) == 15.0

        # Test get_my_salary_details tool
        salary = get_my_salary_details(db, 1, 1, "EMPLOYEE", ROLE_DEFAULT_PERMISSIONS["EMPLOYEE"])
        assert float(salary["base_salary"]) == 25000.00
    finally:
        db.close()
