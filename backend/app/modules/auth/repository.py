"""Auth repository database reads."""

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.modules.auth.models import User


class AuthRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_user(self, user_id: int) -> User | None:
        return self.session.scalar(select(User).where(User.id == user_id))

    def list_active_users(self) -> list[User]:
        return list(self.session.scalars(select(User).where(User.is_active.is_(True)).order_by(User.id)))
