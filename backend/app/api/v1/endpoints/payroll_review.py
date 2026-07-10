"""HR payroll review route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, require_permission
from app.modules.auth.models import User
from app.modules.payroll.schemas import PayrollPreAuditReviewRequest
from app.modules.payroll.services.pre_audit_service import PayrollPreAuditService
from app.shared.response import ok
from app.shared.trace import get_trace_id

router = APIRouter()


@router.get("/records")
def list_payroll_review_records(_=Depends(require_permission("payroll.review.read")), session: Session = Depends(get_db_session)) -> object:
    service = PayrollPreAuditService(session)
    return ok(service.list_records(), get_trace_id())


@router.get("/records/{record_id}")
def get_payroll_review_record(record_id: int, _=Depends(require_permission("payroll.review.read")), session: Session = Depends(get_db_session)) -> object:
    service = PayrollPreAuditService(session)
    return ok(service.get_record(record_id), get_trace_id())


@router.post("/pre-audit")
def review_payroll_pre_audit(
    payload: PayrollPreAuditReviewRequest,
    current_user: User = Depends(require_permission("payroll.review.manage")),
    current_employee=Depends(get_current_employee),
    session: Session = Depends(get_db_session),
) -> object:
    payload.requester_role = current_user.role
    payload.requester_employee_id = current_employee.id
    service = PayrollPreAuditService(session)
    return ok(
        service.review_pre_audit(
            payload,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            actor_employee_id=current_employee.id,
        ),
        get_trace_id(),
    )
