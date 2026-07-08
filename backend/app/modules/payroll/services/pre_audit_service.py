"""Payroll pre-audit display service."""

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules.payroll.repository import PayrollRepository
from app.modules.payroll.schemas import PayrollLineItemRead, PayrollReviewListRead, PayrollReviewRecordRead


class PayrollPreAuditService:
    """Read-only HR payroll review display workflow."""

    def __init__(self, session: Session) -> None:
        self.repository = PayrollRepository(session)

    def list_records(self) -> PayrollReviewListRead:
        records = [
            self._to_record_read(record, employee, period, include_items=False)
            for record, employee, period in self.repository.list_review_records()
        ]
        return PayrollReviewListRead(
            records=records,
            status_note="Sprint 1 仅提供 HR 薪资预审展示外层；权限审计与最终确认待联调。",
        )

    def get_record(self, record_id: int) -> PayrollReviewRecordRead:
        row = self.repository.get_review_record(record_id)
        if row is None:
            raise TalentFlowError("PAYROLL_REVIEW_NOT_FOUND", "薪资预审记录不存在。")
        record, employee, period = row
        return self._to_record_read(record, employee, period, include_items=True)

    def _to_record_read(self, record, employee, period, include_items: bool) -> PayrollReviewRecordRead:
        line_items = []
        if include_items:
            line_items = [
                PayrollLineItemRead(
                    id=item.id,
                    item_type=item.item_type,
                    item_name=item.item_name,
                    amount=item.amount,
                    source_type=item.source_type,
                    source_reference_json=item.source_reference_json or {},
                    calculation_detail_json=item.calculation_detail_json or {},
                )
                for item in self.repository.list_line_items(record.id)
            ]
        return PayrollReviewRecordRead(
            id=record.id,
            employee_id=record.employee_id,
            employee_name=employee.full_name if employee else None,
            payroll_period_id=record.payroll_period_id,
            period_code=period.period_code if period else None,
            status=record.status,
            base_salary_snapshot=record.base_salary_snapshot,
            standard_work_days_snapshot=record.standard_work_days_snapshot,
            total_earnings=record.total_earnings,
            total_deductions=record.total_deductions,
            net_salary_preview=record.net_salary_preview,
            calculation_snapshot=record.calculation_snapshot or {},
            confirmed_at=record.confirmed_at,
            permission_status="权限审计待联调",
            line_items=line_items,
        )
