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
from app.modules.audit.service import AuditLogService


class PayrollPreAuditService:
    """Read-only HR payroll review display workflow."""

    def __init__(self, session: Session) -> None:
        self.repository = PayrollRepository(session)
        self.audit_service = AuditLogService(session)

    def list_records(
        self,
        actor_user_id: int,
        actor_role: str,
        actor_permissions: list[str],
        actor_employee_id: int | None,
    ) -> PayrollReviewListRead:
        allowed_records = []
        for record, employee, period in self.repository.list_review_records():
            policy_res = self._check_record_policy(
                actor_role=actor_role,
                actor_employee_id=actor_employee_id,
                target_employee=employee,
                permissions=actor_permissions,
            )
            if policy_res.get("allowed", False):
                accessible_fields = policy_res.get("accessible_fields", [])
                rec_read = self._to_record_read(
                    record, employee, period, include_items=False, accessible_fields=accessible_fields
                )
                allowed_records.append(rec_read)

        self.audit_service.log_action(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            target_employee_id=actor_employee_id,
            action="LIST_PAYROLL_REVIEWS",
            resource_type="PAYROLL_REVIEW",
            requested_fields=[],
            result="SUCCESS",
            reason=f"列出 {len(allowed_records)} 条已授权的薪资预审记录",
        )

        return PayrollReviewListRead(
            records=allowed_records,
            status_note="薪资预审记录已汇总，已应用字段级数据脱敏与行级权限控制。",
        )

    def get_record(
        self,
        record_id: int,
        actor_user_id: int,
        actor_role: str,
        actor_permissions: list[str],
        actor_employee_id: int | None,
    ) -> PayrollReviewRecordRead:
        row = self.repository.get_review_record(record_id)
        if row is None:
            raise TalentFlowError("PAYROLL_REVIEW_NOT_FOUND", "薪资预审记录不存在。")
        record, employee, period = row

        policy_res = self._check_record_policy(
            actor_role=actor_role,
            actor_employee_id=actor_employee_id,
            target_employee=employee,
            permissions=actor_permissions,
        )
        if not policy_res.get("allowed", False):
            self.audit_service.log_action(
                actor_user_id=actor_user_id,
                actor_role=actor_role,
                target_employee_id=employee.id if employee else None,
                action="QUERY_PAYROLL_REVIEW",
                resource_type="PAYROLL_REVIEW",
                resource_id=record_id,
                result="DENIED",
                reason=policy_res.get("reason", "无权限"),
            )
            raise TalentFlowError("PERMISSION_DENIED", policy_res.get("reason", "您没有权限查看该记录。"), 403)

        accessible_fields = policy_res.get("accessible_fields", [])

        self.audit_service.log_action(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            target_employee_id=employee.id if employee else None,
            action="QUERY_PAYROLL_REVIEW",
            resource_type="PAYROLL_REVIEW",
            resource_id=record_id,
            requested_fields=accessible_fields,
            result="SUCCESS",
            reason=policy_res.get("reason", "允许查询"),
        )

        return self._to_record_read(
            record, employee, period, include_items=True, accessible_fields=accessible_fields
        )

    def review_pre_audit(
        self,
        payload: PayrollPreAuditReviewRequest,
        actor_user_id: int,
        actor_role: str,
        actor_employee_id: int | None,
    ) -> PayrollPreAuditReviewResponse:
        from app.modules.auth.models import User
        from app.core.dependencies import normalize_permissions
        user = self.repository.session.get(User, actor_user_id)
        permissions = list(normalize_permissions(user.permissions)) if user else []

        # Pre-calculate deductions for the target records (strictly read-only on attendance table)
        for record, employee, period in self.repository.list_review_records():
            if not payload.target_record_ids or record.id in payload.target_record_ids:
                if period:
                    self._calculate_attendance_deductions(record, period)

        # Apply row-level policy validation and field masking to records
        records = []
        for record, employee, period in self.repository.list_review_records():
            if not payload.target_record_ids or record.id in payload.target_record_ids:
                policy_res = self._check_record_policy(
                    actor_role=actor_role,
                    actor_employee_id=actor_employee_id,
                    target_employee=employee,
                    permissions=permissions,
                )
                if policy_res.get("allowed", False):
                    rec_read = self._to_record_read(
                        record,
                        employee,
                        period,
                        include_items=payload.include_line_items,
                        accessible_fields=policy_res.get("accessible_fields", []),
                    )
                    records.append(rec_read)

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

        response = PayrollPreAuditReviewResponse(
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
        self.audit_service.log_action(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            target_employee_id=actor_employee_id,
            action="PRE_AUDIT_PAYROLL",
            resource_type="PAYROLL_REVIEW",
            requested_fields=[],
            result="SUCCESS",
            reason=response.message,
        )
        return response

    def _calculate_attendance_deductions(self, record, period) -> None:
        from sqlalchemy import func
        from app.modules.attendance.service import AttendanceService
        from app.modules.payroll.models import PayrollLineItem

        # Fetch monthly attendance summary from the attendance service
        attendance_service = AttendanceService(self.repository.session)
        summary = attendance_service.get_monthly_summary(
            employee_id=record.employee_id,
            year=period.start_date.year,
            month=period.start_date.month,
        )

        late_count = summary.get("late_count", 0)
        early_leave_count = summary.get("early_leave_count", 0)
        absent_count = summary.get("absent_count", 0)
        unpaid_leave_count = summary.get("unpaid_leave_count", 0)

        daily_rate = record.base_salary_snapshot / record.standard_work_days_snapshot

        deductions = []
        if late_count > 0:
            deductions.append({
                "name": f"迟到扣款 ({late_count}次)",
                "amount": Decimal(str(late_count * 50)),
                "detail": {"formula": "次数 * 50", "count": late_count, "rate": 50}
            })
        if early_leave_count > 0:
            deductions.append({
                "name": f"早退扣款 ({early_leave_count}次)",
                "amount": Decimal(str(early_leave_count * 50)),
                "detail": {"formula": "次数 * 50", "count": early_leave_count, "rate": 50}
            })
        if absent_count > 0:
            absent_deduct = (Decimal(str(absent_count)) * daily_rate).quantize(Decimal("0.01"))
            deductions.append({
                "name": f"缺勤扣款 ({absent_count}天)",
                "amount": absent_deduct,
                "detail": {"formula": "天数 * 日薪", "days": absent_count, "daily_rate": float(daily_rate)}
            })
        if unpaid_leave_count > 0:
            leave_deduct = (Decimal(str(unpaid_leave_count)) * daily_rate).quantize(Decimal("0.01"))
            deductions.append({
                "name": f"无薪假扣款 ({unpaid_leave_count}天)",
                "amount": leave_deduct,
                "detail": {"formula": "天数 * 日薪", "days": unpaid_leave_count, "daily_rate": float(daily_rate)}
            })

        self.repository.session.query(PayrollLineItem).filter(
            PayrollLineItem.payroll_review_record_id == record.id,
            PayrollLineItem.source_type == "ATTENDANCE"
        ).delete()

        for ded in deductions:
            item = PayrollLineItem(
                payroll_review_record_id=record.id,
                item_type="DEDUCTION",
                item_name=ded["name"],
                amount=ded["amount"],
                source_type="ATTENDANCE",
                source_reference_json={},
                calculation_detail_json=ded["detail"]
            )
            self.repository.session.add(item)
        
        self.repository.session.flush()

        earnings_sum = self.repository.session.query(
            func.coalesce(func.sum(PayrollLineItem.amount), 0)
        ).filter(
            PayrollLineItem.payroll_review_record_id == record.id,
            PayrollLineItem.item_type == "EARNING"
        ).scalar()

        deductions_sum = self.repository.session.query(
            func.coalesce(func.sum(PayrollLineItem.amount), 0)
        ).filter(
            PayrollLineItem.payroll_review_record_id == record.id,
            PayrollLineItem.item_type == "DEDUCTION"
        ).scalar()

        record.total_earnings = Decimal(str(earnings_sum))
        record.total_deductions = Decimal(str(deductions_sum))
        record.net_salary_preview = max(Decimal("0"), record.total_earnings - record.total_deductions)
        
        self.repository.session.add(record)
        self.repository.session.commit()

    def _check_record_policy(
        self,
        actor_role: str,
        actor_employee_id: int | None,
        target_employee,
        permissions: list[str],
    ) -> dict[str, Any]:
        if target_employee is None:
            return {"allowed": False, "reason": "目标员工档案不存在"}

        relation = "none"
        if actor_employee_id == target_employee.id:
            relation = "self"
        elif target_employee.manager_employee_id == actor_employee_id:
            relation = "manager"
        else:
            from app.modules.employee.models import Employee
            actor_emp = self.repository.session.query(Employee).filter(Employee.id == actor_employee_id).first()
            if actor_emp and actor_role == "DEPARTMENT_MANAGER" and target_employee.department == actor_emp.department:
                relation = "manager"

        from app.modules.payroll.services.access_service import load_human_only_function, SALARY_ACCESS_CONTRACT
        check_fn = load_human_only_function(SALARY_ACCESS_CONTRACT)
        if check_fn is None:
            return {"allowed": False, "reason": "安全算法未就绪"}

        try:
            return check_fn(
                actor_role=actor_role,
                actor_employee_id=actor_employee_id,
                target_employee_id=target_employee.id,
                permissions=permissions,
                relation=relation,
            )
        except Exception as exc:
            return {"allowed": False, "reason": f"权限算法执行出错: {str(exc)}"}

    def _to_record_read(
        self,
        record,
        employee,
        period,
        include_items: bool,
        accessible_fields: list[str],
    ) -> PayrollReviewRecordRead:
        line_items = []
        has_salary_access = "base_salary" in accessible_fields

        if include_items:
            line_items = [
                PayrollLineItemRead(
                    id=item.id,
                    item_type=item.item_type,
                    item_name=item.item_name,
                    amount=item.amount if has_salary_access else Decimal("0.00"),
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
            base_salary_snapshot=record.base_salary_snapshot if has_salary_access else Decimal("0.00"),
            standard_work_days_snapshot=record.standard_work_days_snapshot,
            total_earnings=record.total_earnings if has_salary_access else Decimal("0.00"),
            total_deductions=record.total_deductions if has_salary_access else Decimal("0.00"),
            net_salary_preview=record.net_salary_preview if has_salary_access else Decimal("0.00"),
            calculation_snapshot=record.calculation_snapshot or {},
            confirmed_at=record.confirmed_at,
            permission_status="已完成安全审计",
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
