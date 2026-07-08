from sqlalchemy.orm import Session
from app.modules.employee.repository import EmployeeRepository
from app.modules.employee.models import Employee, LeaveBalance


class EmployeeService:
    def __init__(self, db: Session) -> None:
        self.repo = EmployeeRepository(db)

    def get_employee_by_id(self, employee_id: int) -> Employee | None:
        return self.repo.get_by_id(employee_id)

    def get_employee_by_user_id(self, user_id: int) -> Employee | None:
        return self.repo.get_by_user_id(user_id)

    def get_employee_leave_balance(self, employee_id: int, year: int) -> LeaveBalance | None:
        return self.repo.get_leave_balance(employee_id, year)
