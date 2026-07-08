"""Employee repository database reads."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.employee.models import Employee, LeaveBalance


class EmployeeRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.db = session

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.session.query(Employee).filter(Employee.id == employee_id).first()

    def get_by_user_id(self, user_id: int) -> Employee | None:
        return self.session.query(Employee).filter(Employee.user_id == user_id).first()

    def get_by_employee_no(self, employee_no: str) -> Employee | None:
        return self.session.query(Employee).filter(Employee.employee_no == employee_no).first()

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
