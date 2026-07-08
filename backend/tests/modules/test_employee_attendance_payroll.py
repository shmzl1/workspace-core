import pytest
from datetime import date
from fastapi.testclient import TestClient
from app.main import app
from app.core.database import SessionLocal
from app.modules.attendance.models import AttendanceRecord
from app.modules.audit.models import AuditLog

client = TestClient(app)


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
