"""Audit repository database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.audit.models import AuditLog


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_logs(self, limit: int = 50) -> list[AuditLog]:
        return list(self.session.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)))
