"""Audit repository database access."""

from sqlalchemy import select
from sqlalchemy.orm import Session
from app.modules.audit.models import AuditLog


class AuditLogRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.db = session

    def save_log(self, log: AuditLog) -> AuditLog:
        self.session.add(log)
        self.session.commit()
        self.session.refresh(log)
        return log

    def list_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return self.session.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()


class AuditRepository:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.db = session

    def list_logs(self, limit: int = 50) -> list[AuditLog]:
        return list(self.session.scalars(select(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit)))
