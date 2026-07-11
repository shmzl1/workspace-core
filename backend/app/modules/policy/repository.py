"""Policy document persistence boundary."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.policy.models import PolicyDocument


class PolicyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def list_active(self, query: str | None = None) -> list[PolicyDocument]:
        statement = select(PolicyDocument).where(PolicyDocument.is_active.is_(True))
        if query:
            pattern = f"%{query.strip()}%"
            statement = statement.where(PolicyDocument.title.ilike(pattern))
        return list(self.session.scalars(statement.order_by(PolicyDocument.updated_at.desc(), PolicyDocument.id.desc())))
