"""Payroll pre-audit display service."""

from decimal import Decimal
from typing import Any

from sqlalchemy.orm import Session

from app.core.exceptions import TalentFlowError
from app.modules.payroll.repository import PayrollRepository
from app.modules.payroll.schemas import (
    PayrollLineItemRead,
    PayrollPreAuditReviewRequest,
    PayrollPreAuditReviewResponse,
    PayrollReviewListRead,
    PayrollReviewRecordRead,
)
from app.modules.payroll.services.access_service import PayrollAccessService


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
            status_note="薪资预审记录已汇总，权限风险以服务端预审结果为准。",
        )

    def get_record(self, record_id: int) -> PayrollReviewRecordRead:
        row = self.repository.get_review_record(record_id)
        if row is None:
            raise TalentFlowError("PAYROLL_REVIEW_NOT_FOUND", "薪资预审记录不存在。")
        record, employee, period = row
        return self._to_record_read(record, employee, period, include_items=True)

    def review_pre_audit(self, payload: PayrollPreAuditReviewRequest) -> PayrollPreAuditReviewResponse:
        records = [
            self._to_record_read(record, employee, period, include_items=payload.include_line_items)
            for record, employee, period in self.repository.list_review_records()
            if not payload.target_record_ids or record.id in payload.target_record_ids
        ]
        access_payload = {
            "requester": {
                "role": payload.requester_role,
                "employee_id": payload.requester_employee_id,
            },
            "records": [self._to_algorithm_record(record) for record in records],
        }
        result = PayrollAccessService().check_salary_access(access_payload)
        if result.get("status") == "algorithm_not_ready":
            return PayrollPreAuditReviewResponse(
                status=result["status"],
                message=result["message"],
                pending_batches=len(records),
                expected_module=result["expected_module"],
                expected_function=result["expected_function"],
                fallback_data=result.get("fallback_data", {}),
                requires_human_only=True,
            )

        return PayrollPreAuditReviewResponse(
            status=result.get("status", "reviewed"),
            message=result.get("message", "薪资预审结果已生成。"),
            pending_batches=result.get("pending_batches", len(records)),
            abnormal_salary_items=result.get("abnormal_salary_items", []),
            permission_risks=result.get("permission_risks", []),
            deduction_sources=result.get("deduction_sources", []),
            approval_suggestion=result.get("approval_suggestion"),
            risk_level=result.get("risk_level"),
            requires_human_only=False,
        )

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
            permission_status="等待权限复核",
            line_items=line_items,
        )

    @classmethod
    def _to_algorithm_record(cls, record: PayrollReviewRecordRead) -> dict[str, Any]:
        return {
            "id": record.id,
            "employee_id": record.employee_id,
            "employee_name": record.employee_name,
            "period_code": record.period_code,
            "status": record.status,
            "base_salary_snapshot": cls._json_ready(record.base_salary_snapshot),
            "total_earnings": cls._json_ready(record.total_earnings),
            "total_deductions": cls._json_ready(record.total_deductions),
            "net_salary_preview": cls._json_ready(record.net_salary_preview),
            "calculation_snapshot": cls._json_ready(record.calculation_snapshot),
            "line_items": [cls._json_ready(item.model_dump()) for item in record.line_items],
        }

    @classmethod
    def _json_ready(cls, value: Any) -> Any:
        if isinstance(value, dict):
            return {key: cls._json_ready(item) for key, item in value.items()}
        if isinstance(value, list):
            return [cls._json_ready(item) for item in value]
        if isinstance(value, Decimal):
            return float(value)
        if hasattr(value, "isoformat"):
            return value.isoformat()
        return value
