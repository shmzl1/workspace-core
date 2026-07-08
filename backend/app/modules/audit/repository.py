from sqlalchemy.orm import Session
from app.modules.audit.models import AuditLog


class AuditLogRepository:
    def __init__(self, db: Session) -> None:
        self.db = db

    def save_log(self, log: AuditLog) -> AuditLog:
        self.db.add(log)
        self.db.commit()
        self.db.refresh(log)
        return log

    def list_logs(self, limit: int = 100, offset: int = 0) -> list[AuditLog]:
        return self.db.query(AuditLog).order_by(AuditLog.created_at.desc()).limit(limit).offset(offset).all()
