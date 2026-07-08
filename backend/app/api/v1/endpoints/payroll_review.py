"""HR payroll review route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.payroll.services.pre_audit_service import PayrollPreAuditService
from app.shared.response import ok
from app.shared.trace import get_trace_id

router = APIRouter()


@router.get("/records")
def list_payroll_review_records(session: Session = Depends(get_db_session)) -> object:
    service = PayrollPreAuditService(session)
    return ok(service.list_records(), get_trace_id())


@router.get("/records/{record_id}")
def get_payroll_review_record(record_id: int, session: Session = Depends(get_db_session)) -> object:
    service = PayrollPreAuditService(session)
    return ok(service.get_record(record_id), get_trace_id())
