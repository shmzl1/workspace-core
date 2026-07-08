import os
os.environ["DATABASE_URL"] = "sqlite+pysqlite:///test.db"

import pytest
from datetime import date
from decimal import Decimal
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import Base, engine, SessionLocal

from app.modules.auth.models import User
from app.modules.employee.models import Employee, LeaveBalance
from app.modules.payroll.models import SalaryRecord
from app.modules.attendance.models import AttendanceRecord, WorkCalendar
from app.modules.audit.models import AuditLog

from sqlalchemy.ext.compiler import compiles
from sqlalchemy.dialects.postgresql import JSONB

@compiles(JSONB, "sqlite")
def compile_jsonb_sqlite(element, compiler, **kw):
    return "JSON"

client = TestClient(app)


# Initialize schema and seed data if using in-memory SQLite (conftest.py default)
db = SessionLocal()
try:
    if "sqlite" in str(engine.url):
        # Keep only the tables needed for the test to avoid PostgreSQL-specific constraints in other modules
        needed_tables = {
            "users", "employees", "leave_balances", "salary_records", 
            "attendance_records", "audit_logs", "work_calendars"
        }
        for table_name in list(Base.metadata.tables.keys()):
            if table_name not in needed_tables:
                Base.metadata.remove(Base.metadata.tables[table_name])
        
        # Strip PostgreSQL-specific default casts (like ::jsonb) before running create_all
        from sqlalchemy import text
        for table in Base.metadata.tables.values():
            for column in table.columns:
                if column.server_default is not None:
                    arg_str = str(column.server_default.arg)
                    if "::jsonb" in arg_str:
                        new_default = arg_str.replace("::jsonb", "")
                        column.server_default.arg = text(new_default)
        Base.metadata.create_all(bind=engine)


        # Seed mock data for tests
        user1 = User(id=1, username="zhangwei", password_hash="hash", role="EMPLOYEE", is_active=True)
        user2 = User(id=2, username="liming", password_hash="hash", role="DEPARTMENT_MANAGER", is_active=True)
        user3 = User(id=3, username="linyuqing", password_hash="hash", role="HR_SPECIALIST", is_active=True)
        user4 = User(id=4, username="wangqiang", password_hash="hash", role="PAYROLL_ADMIN", is_active=True)
        db.add_all([user1, user2, user3, user4])
        db.commit()
        
        emp1 = Employee(id=1, user_id=1, employee_no="EMP001", full_name="张伟", department="研发部", job_title="高级工程师", employment_status="ACTIVE")
        emp2 = Employee(id=2, user_id=2, employee_no="EMP002", full_name="李明", department="研发部", job_title="研发主管", employment_status="ACTIVE")
        emp3 = Employee(id=3, user_id=3, employee_no="EMP003", full_name="林雨晴", department="人事部", job_title="HR专员", employment_status="ACTIVE")
        emp4 = Employee(id=4, user_id=4, employee_no="EMP004", full_name="王强", department="财务部", job_title="薪酬管理员", employment_status="ACTIVE")
        db.add_all([emp1, emp2, emp3, emp4])
        db.commit()
        
        sal1 = SalaryRecord(id=1, employee_id=1, base_salary=Decimal("25000.00"), currency="CNY", effective_from=date(2026, 1, 1))
        sal2 = SalaryRecord(id=2, employee_id=2, base_salary=Decimal("35000.00"), currency="CNY", effective_from=date(2026, 1, 1))
        db.add_all([sal1, sal2])
        db.commit()
        
        leave1 = LeaveBalance(id=1, employee_id=1, leave_type="ANNUAL", year=2026, total_days=Decimal("15.00"), used_days=Decimal("3.00"))
        db.add(leave1)
        db.commit()
finally:
    db.close()



def test_get_me():
    # Test getting current employee profile for zhangwei
    headers = {"X-Mock-User-Id": "1", "X-Mock-Role": "EMPLOYEE"}
    response = client.get("/api/v1/employees/me", headers=headers)
    assert response.status_code == 200
    data = response.json()
    assert data["success"] is True
    assert data["data"]["employee"]["full_name"] == "张伟"
    assert data["data"]["employee"]["employee_no"] == "EMP001"


def test_attendance_flow():
    # Test checking in and out, duplicate check warnings
    headers = {"X-Mock-User-Id": "1", "X-Mock-Role": "EMPLOYEE"}
    
    # 1. Clear today's record from DB for a clean test run
    db = SessionLocal()
    try:
        db.query(AttendanceRecord).filter(
            AttendanceRecord.employee_id == 1,
            AttendanceRecord.attendance_date == date.today()
        ).delete()
        db.commit()
    finally:
        db.close()
        
    # 2. Get today's record initially - should be None
    response = client.get("/api/v1/attendance/today", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"] is None
    
    # 3. Check-in - should succeed
    response = client.post("/api/v1/attendance/check-in", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["record"]["check_in_at"] is not None
    
    # 4. Duplicate Check-in - should fail
    response = client.post("/api/v1/attendance/check-in", headers=headers)
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "DUPLICATE_CHECK_IN"
    
    # 5. Check-out - should succeed
    response = client.post("/api/v1/attendance/check-out", headers=headers)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert response.json()["data"]["record"]["check_out_at"] is not None
    
    # 6. Duplicate Check-out - should fail
    response = client.post("/api/v1/attendance/check-out", headers=headers)
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "DUPLICATE_CHECK_OUT"
    
    # 7. Today's attendance - should be complete
    response = client.get("/api/v1/attendance/today", headers=headers)
    assert response.status_code == 200
    assert response.json()["data"]["check_in_at"] is not None
    assert response.json()["data"]["check_out_at"] is not None


def test_payroll_access():
    # 1. zhangwei (EMPLOYEE) queries own salary - Allowed
    headers_self = {"X-Mock-User-Id": "1", "X-Mock-Role": "EMPLOYEE"}
    response = client.get("/api/v1/payroll/me", headers=headers_self)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert float(response.json()["data"]["base_salary"]) == 25000.00
    
    # 2. zhangwei (EMPLOYEE) queries liming's salary (id=2) - Denied
    response = client.get("/api/v1/payroll/employee/2", headers=headers_self)
    assert response.status_code == 400
    assert response.json()["success"] is False
    assert response.json()["error"]["code"] == "PERMISSION_DENIED"
    
    # 3. liming (DEPARTMENT_MANAGER) queries zhangwei's salary (id=1, same department) - Allowed with masking
    headers_manager = {"X-Mock-User-Id": "2", "X-Mock-Role": "DEPARTMENT_MANAGER"}
    response = client.get("/api/v1/payroll/employee/1", headers=headers_manager)
    assert response.status_code == 200
    assert response.json()["success"] is True
    data = response.json()["data"]
    assert float(data["base_salary"]) == 25000.00
    assert data["effective_to"] is None  # Masked/None for managers
    
    # 4. wangqiang (PAYROLL_ADMIN) queries zhangwei's salary - Allowed with all fields
    headers_admin = {"X-Mock-User-Id": "4", "X-Mock-Role": "PAYROLL_ADMIN"}
    response = client.get("/api/v1/payroll/employee/1", headers=headers_admin)
    assert response.status_code == 200
    assert response.json()["success"] is True
    assert float(response.json()["data"]["base_salary"]) == 25000.00


def test_audit_logs():
    # linyuqing (HR_SPECIALIST) retrieves audit logs
    headers_hr = {"X-Mock-User-Id": "3", "X-Mock-Role": "HR_SPECIALIST"}
    response = client.get("/api/v1/audit/logs", headers=headers_hr)
    assert response.status_code == 200
    assert response.json()["success"] is True
    logs = response.json()["data"]
    assert len(logs) > 0
    # Validate the structure of logged actions
    actions = [l["action"] for l in logs]
    assert "QUERY_SALARY" in actions


@pytest.fixture(scope="session", autouse=True)
def cleanup_test_db():
    yield
    import os
    if os.path.exists("test.db"):
        try:
            os.remove("test.db")
        except OSError:
            pass

