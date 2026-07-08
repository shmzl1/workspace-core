"""Audit route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.modules.audit.service import AuditService
from app.shared.response import ok

router = APIRouter()


def get_audit_service(session: Session = Depends(get_db_session)) -> AuditService:
    return AuditService.from_session(session)


@router.get("/logs")
def list_logs(limit: int = 50, service: AuditService = Depends(get_audit_service)) -> object:
    return ok(service.list_logs(limit))
