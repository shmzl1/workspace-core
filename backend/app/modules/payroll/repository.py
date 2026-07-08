"""Payroll repository database reads.

Repositories own database reads and writes only. Salary access checks must be
orchestrated by services before repository access.
"""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.payroll.models import SalaryRecord


class PayrollRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_latest_salary(self, employee_id: int) -> SalaryRecord | None:
        return self.session.scalar(
            select(SalaryRecord)
            .where(SalaryRecord.employee_id == employee_id)
            .order_by(SalaryRecord.effective_from.desc(), SalaryRecord.id.desc())
            .limit(1)
        )
