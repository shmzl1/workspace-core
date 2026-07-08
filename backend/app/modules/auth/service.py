"""Auth service for demo identity context."""

from app.core.security import DemoIdentity
from app.modules._serialization import model_to_dict
from app.modules.auth.repository import AuthRepository
from sqlalchemy.orm import Session


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "AuthService":
        return cls(AuthRepository(session))

    def current_context(self, identity: DemoIdentity) -> dict:
        user = self.repository.get_user(identity.user_id)
        data = {
            "identity": {
                "user_id": identity.user_id,
                "username": identity.username,
                "role": identity.role,
                "employee_id": identity.employee_id,
            },
            "source": "X-Demo-Identity",
        }
        if user:
            data["user"] = model_to_dict(user, ["id", "username", "role", "is_active"])
        return data

    def list_demo_users(self) -> list[dict]:
        return [model_to_dict(user, ["id", "username", "role", "is_active"]) for user in self.repository.list_active_users()]
