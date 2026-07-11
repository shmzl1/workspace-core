"""Employee service read boundary."""

from sqlalchemy.orm import Session
from app.core.exceptions import TalentFlowError
from app.modules._serialization import model_to_dict
from app.modules.employee.repository import EmployeeRepository
from app.modules.employee.models import Employee, LeaveBalance

EMPLOYEE_FIELDS = [
    "id",
    "user_id",
    "employee_no",
    "full_name",
    "department",
    "job_title",
    "manager_employee_id",
    "email",
    "phone",
    "hire_date",
    "employment_status",
]


class EmployeeService:
    def __init__(self, repository_or_session) -> None:
        if isinstance(repository_or_session, Session):
            self.repository = EmployeeRepository(repository_or_session)
        else:
            self.repository = repository_or_session
        self.repo = self.repository

    @classmethod
    def from_session(cls, session: Session) -> "EmployeeService":
        return cls(EmployeeRepository(session))

    def get_employee_by_id(self, employee_id: int) -> Employee | None:
        return self.repository.get_by_id(employee_id)

    def get_employee_by_user_id(self, user_id: int) -> Employee | None:
        return self.repository.get_by_user_id(user_id)

    def get_employee_leave_balance(self, employee_id: int, year: int) -> LeaveBalance | None:
        return self.repository.get_leave_balance(employee_id, year)

    def get_employee(self, employee_id: int) -> dict:
        employee = self.repository.get_employee(employee_id)
        if employee is None:
            raise TalentFlowError("EMPLOYEE_NOT_FOUND", "员工不存在", 404)
        return model_to_dict(employee, EMPLOYEE_FIELDS)

    def list_employees(self) -> list[dict]:
        return [model_to_dict(employee, EMPLOYEE_FIELDS) for employee in self.repository.list_employees()]

    def get_annual_leave(self, employee_id: int, year: int) -> dict:
        balance = self.repository.get_leave_balance(employee_id, year)
        if balance is None:
            return {"employee_id": employee_id, "year": year, "leave_type": "ANNUAL", "total_days": "0", "used_days": "0"}
        return model_to_dict(balance, ["id", "employee_id", "leave_type", "year", "total_days", "used_days"])

    def get_leave_overview(self, employee_id: int, year: int) -> dict:
        balances = [model_to_dict(item, ["id", "employee_id", "leave_type", "year", "total_days", "used_days"]) for item in self.repository.list_leave_balances(employee_id, year)]
        requests = [model_to_dict(item, ["id", "leave_type", "start_at", "end_at", "duration_hours", "reason", "status", "approved_at"]) for item in self.repository.list_leave_requests(employee_id)]
        return {"balances": balances, "requests": requests}
