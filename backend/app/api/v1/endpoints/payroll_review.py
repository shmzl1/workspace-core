"""HR payroll review route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_employee, require_any_permission, require_permission, user_permissions
from app.modules.auth.models import User
from app.modules.payroll.schemas import PayrollPreAuditReviewRequest
from app.modules.payroll.services.pre_audit_service import PayrollPreAuditService
from app.shared.response import ok
from app.shared.trace import get_trace_id

router = APIRouter()


@router.get("/records")
def list_payroll_review_records(
    current_user: User = Depends(require_any_permission("payroll.review.read", "payroll.all.read")),
    current_employee=Depends(get_current_employee),
    session: Session = Depends(get_db_session),
) -> object:
    service = PayrollPreAuditService(session)
    permissions = list(user_permissions(current_user))
    return ok(
        service.list_records(
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            actor_permissions=permissions,
            actor_employee_id=current_employee.id,
        ),
        get_trace_id(),
    )


@router.get("/records/{record_id}")
def get_payroll_review_record(
    record_id: int,
    current_user: User = Depends(require_permission("payroll.review.read")),
    current_employee=Depends(get_current_employee),
    session: Session = Depends(get_db_session),
) -> object:
    service = PayrollPreAuditService(session)
    permissions = list(user_permissions(current_user))
    return ok(
        service.get_record(
            record_id,
            actor_user_id=current_user.id,
            actor_role=current_user.role,
            actor_permissions=permissions,
            actor_employee_id=current_employee.id,
        ),
        get_trace_id(),
    )


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

