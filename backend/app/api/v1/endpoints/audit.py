"""Audit route boundary."""

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.modules.audit.schemas import AuditLogRead
from app.modules.audit.service import AuditLogService, AuditService
from app.shared.response import ApiResponse, ok

router = APIRouter()


def get_audit_service(session: Session = Depends(get_db_session)) -> AuditService:
    return AuditService.from_session(session)


@router.get("/logs", response_model=ApiResponse[list[AuditLogRead]])
def list_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    _=Depends(require_permission("audit.read")),
    db: Session = Depends(get_db_session),
) -> ApiResponse[list[AuditLogRead]]:
    """Retrieve audit logs for accounts granted audit.read."""
    service = AuditLogService(db)
    logs = service.list_logs(limit, offset)
    data = [AuditLogRead.model_validate(log) for log in logs]
    return ok(data)
