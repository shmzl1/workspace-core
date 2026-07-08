"""Audit service read/write boundary."""

from sqlalchemy.orm import Session
from app.modules._serialization import model_to_dict
from app.modules.audit.models import AuditLog
from app.modules.audit.repository import AuditLogRepository, AuditRepository
from app.shared.trace import get_trace_id


class AuditLogService:
    def __init__(self, repository_or_session) -> None:
        if isinstance(repository_or_session, Session):
            self.repository = AuditLogRepository(repository_or_session)
            self.db = repository_or_session
        else:
            self.repository = repository_or_session
            self.db = repository_or_session.session
        self.repo = self.repository

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


class AuditService:
    def __init__(self, repository_or_session) -> None:
        if isinstance(repository_or_session, Session):
            self.repository = AuditRepository(repository_or_session)
        else:
            self.repository = repository_or_session
        self.repo = self.repository

    @classmethod
    def from_session(cls, session: Session) -> "AuditService":
        return cls(AuditRepository(session))

    def list_logs(self, limit: int = 50) -> list[dict]:
        fields = [
            "id",
            "actor_user_id",
            "actor_role",
            "target_employee_id",
            "action",
            "resource_type",
            "resource_id",
            "requested_fields",
            "result",
            "reason",
            "trace_id",
            "created_at",
        ]
        return [model_to_dict(log, fields) for log in self.repository.list_logs(limit)]
