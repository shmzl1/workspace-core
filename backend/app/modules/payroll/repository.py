"""Payroll repository boundary."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.employee.models import Employee
from app.modules.payroll.models import PayrollLineItem, PayrollPeriod, PayrollReviewRecord


class PayrollRepository:
    """Database reads for payroll review display."""

    def __init__(self, session: Session) -> None:
        self.session = session

    def list_review_records(self) -> list[tuple[PayrollReviewRecord, Employee | None, PayrollPeriod | None]]:
        rows = self.session.execute(
            select(PayrollReviewRecord, Employee, PayrollPeriod)
            .join(Employee, Employee.id == PayrollReviewRecord.employee_id, isouter=True)
            .join(PayrollPeriod, PayrollPeriod.id == PayrollReviewRecord.payroll_period_id, isouter=True)
            .order_by(PayrollReviewRecord.id)
        )
        return [(record, employee, period) for record, employee, period in rows.all()]

    def get_review_record(
        self,
        record_id: int,
    ) -> tuple[PayrollReviewRecord, Employee | None, PayrollPeriod | None] | None:
        row = self.session.execute(
            select(PayrollReviewRecord, Employee, PayrollPeriod)
            .join(Employee, Employee.id == PayrollReviewRecord.employee_id, isouter=True)
            .join(PayrollPeriod, PayrollPeriod.id == PayrollReviewRecord.payroll_period_id, isouter=True)
            .where(PayrollReviewRecord.id == record_id)
        ).one_or_none()
        if row is None:
            return None
        record, employee, period = row
        return record, employee, period

    def list_line_items(self, review_record_id: int) -> list[PayrollLineItem]:
        return list(
            self.session.scalars(
                select(PayrollLineItem)
                .where(PayrollLineItem.payroll_review_record_id == review_record_id)
                .order_by(PayrollLineItem.id)
            ).all()
        )
