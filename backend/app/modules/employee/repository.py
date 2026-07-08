"""Employee repository database reads."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.employee.models import Employee, LeaveBalance


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_employee(self, employee_id: int) -> Employee | None:
        return self.session.scalar(select(Employee).where(Employee.id == employee_id))

    def list_employees(self) -> list[Employee]:
        return list(self.session.scalars(select(Employee).order_by(Employee.id)))

    def get_leave_balance(self, employee_id: int, year: int) -> LeaveBalance | None:
        return self.session.scalar(
            select(LeaveBalance).where(
                LeaveBalance.employee_id == employee_id,
                LeaveBalance.year == year,
                LeaveBalance.leave_type == "ANNUAL",
            )
        )
