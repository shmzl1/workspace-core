"""Audit route boundary."""

from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.modules.audit.schemas import AuditLogRead
from app.modules.audit.service import AuditLogService
from app.modules.auth.models import User
from app.shared.response import ApiResponse, ok

router = APIRouter()


@router.get("/logs", response_model=ApiResponse[list[AuditLogRead]])
def list_logs(
    limit: int = Query(default=100, ge=1, le=1000),
    offset: int = Query(default=0, ge=0),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> ApiResponse[list[AuditLogRead]]:
    """Retrieve system audit logs. Only accessible to HR Specialists and Payroll Admins."""
    if current_user.role not in ("HR_SPECIALIST", "PAYROLL_ADMIN"):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="无权访问系统审计日志"
        )
    
    service = AuditLogService(db)
    logs = service.list_logs(limit, offset)
    data = [AuditLogRead.model_validate(log) for log in logs]
    return ok(data)
