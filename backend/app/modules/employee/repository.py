from sqlalchemy.orm import Session
from app.modules.employee.models import Employee, LeaveBalance


class EmployeeRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def get_by_id(self, employee_id: int) -> Employee | None:
        return self.db.query(Employee).filter(Employee.id == employee_id).first()

    def get_by_user_id(self, user_id: int) -> Employee | None:
        return self.db.query(Employee).filter(Employee.user_id == user_id).first()

    def get_by_employee_no(self, employee_no: str) -> Employee | None:
        return self.db.query(Employee).filter(Employee.employee_no == employee_no).first()

    def get_leave_balance(self, employee_id: int, year: int) -> LeaveBalance | None:
        return self.db.query(LeaveBalance).filter(
            LeaveBalance.employee_id == employee_id,
            LeaveBalance.year == year,
            LeaveBalance.leave_type == "ANNUAL"
        ).first()
