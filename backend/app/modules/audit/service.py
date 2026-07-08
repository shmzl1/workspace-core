from sqlalchemy.orm import Session
from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditLogRepository
from app.shared.trace import get_trace_id


class AuditLogService:
    def __init__(self, db: Session) -> None:
        self.repo = AuditLogRepository(db)

    def log_action(
        self,
        actor_user_id: int | None,
        actor_role: str,
        target_employee_id: int | None,
        action: str,
        resource_type: str,
        resource_id: int | None = None,
        requested_fields: list[str] | None = None,
        result: str = "SUCCESS",
        reason: str | None = None,
        ip_address: str | None = None,
        user_agent: str | None = None
    ) -> AuditLog:
        """Create and persist a new audit log entry."""
        trace_id = get_trace_id()
        
        log = AuditLog(
            actor_user_id=actor_user_id,
            actor_role=actor_role,
            target_employee_id=target_employee_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            requested_fields=requested_fields or [],
            result=result,
            reason=reason,
            trace_id=trace_id,
            ip_address=ip_address,
            user_agent=user_agent
        )
        return self.repo.save_log(log)

    def list_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return self.repo.list_logs(limit, offset)
