from datetime import date, datetime
from decimal import Decimal
from types import SimpleNamespace

import pytest

from app.core.exceptions import TalentFlowError
from app.modules.employee.service import EmployeeService


class FakeEmployeeRepository:
    def __init__(self) -> None:
        self.employee = None
        self.balance = None
        self.balances = []
        self.requests = []

    def get_employee(self, employee_id: int):
        return self.employee

    def list_employees(self):
        return [self.employee] if self.employee is not None else []

    def get_leave_balance(self, employee_id: int, year: int):
        return self.balance

    def list_leave_balances(self, employee_id: int, year: int):
        return self.balances

    def list_leave_requests(self, employee_id: int):
        return self.requests


def employee() -> SimpleNamespace:
    return SimpleNamespace(
        id=7,
        user_id=17,
        employee_no="EMP-007",
        full_name="Ada Lovelace",
        department="Engineering",
        job_title="Backend Engineer",
        manager_employee_id=None,
        email="ada@example.test",
        phone="10086",
        hire_date=date(2025, 1, 1),
        employment_status="ACTIVE",
    )


def test_annual_leave_returns_zero_default_when_no_balance_exists() -> None:
    service = EmployeeService(FakeEmployeeRepository())

    assert service.get_annual_leave(7, 2026) == {
        "employee_id": 7,
        "year": 2026,
        "leave_type": "ANNUAL",
        "total_days": "0",
        "used_days": "0",
    }


def test_employee_and_leave_overview_serialize_business_values() -> None:
    repository = FakeEmployeeRepository()
    repository.employee = employee()
    repository.balances = [
        SimpleNamespace(
            id=1,
            employee_id=7,
            leave_type="ANNUAL",
            year=2026,
            total_days=Decimal("12.5"),
            used_days=Decimal("3.0"),
        )
    ]
    repository.requests = [
        SimpleNamespace(
            id=2,
            leave_type="ANNUAL",
            start_at=datetime(2026, 7, 1, 9, 0),
            end_at=datetime(2026, 7, 1, 18, 0),
            duration_hours=Decimal("8"),
            reason="Vacation",
            status="APPROVED",
            approved_at=datetime(2026, 6, 20, 10, 0),
        )
    ]
    service = EmployeeService(repository)

    assert service.get_employee(7)["hire_date"] == "2025-01-01"
    overview = service.get_leave_overview(7, 2026)
    assert overview["balances"][0]["total_days"] == "12.5"
    assert overview["requests"][0]["start_at"] == "2026-07-01T09:00:00"
    assert overview["requests"][0]["duration_hours"] == "8"


def test_get_employee_raises_not_found_for_missing_employee() -> None:
    service = EmployeeService(FakeEmployeeRepository())

    with pytest.raises(TalentFlowError) as error:
        service.get_employee(7)

    assert error.value.code == "EMPLOYEE_NOT_FOUND"
