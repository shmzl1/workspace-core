"""Audit service read boundary."""

from app.modules._serialization import model_to_dict
from app.modules.audit.repository import AuditRepository
from sqlalchemy.orm import Session


class AuditService:
    def __init__(self, repository: AuditRepository) -> None:
        self.repository = repository

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
