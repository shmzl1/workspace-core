"""Authentication service backed by database users and JWT tokens."""

from datetime import timedelta

from passlib.hash import bcrypt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.exceptions import TalentFlowError
from app.core.security import create_access_token
from app.modules.auth.models import User
from app.modules.auth.permissions import normalize_permissions
from app.modules.auth.repository import AuthRepository
from app.modules.auth.schemas import AuthUserRead, LoginResponse


class AuthService:
    def __init__(self, repository: AuthRepository) -> None:
        self.repository = repository

    @classmethod
    def from_session(cls, session: Session) -> "AuthService":
        return cls(AuthRepository(session))

    def login(self, username: str, password: str) -> LoginResponse:
        user = self.repository.get_by_username(username.strip())
        if user is None or not self._verify_password(password, user.password_hash):
            raise TalentFlowError("INVALID_CREDENTIALS", "用户名或密码错误", 401)
        if not user.is_active:
            raise TalentFlowError("USER_INACTIVE", "账号已停用", 401)
        settings = get_settings()
        token = create_access_token(
            {"sub": user.username, "user_id": user.id, "role": user.role},
            timedelta(minutes=settings.jwt_expire_minutes),
        )
        return LoginResponse(
            access_token=token,
            expires_in=settings.jwt_expire_minutes * 60,
            user=self.user_read(user),
        )

    def get_current_user(self, user: User) -> AuthUserRead:
        if not user.is_active:
            raise TalentFlowError("USER_INACTIVE", "账号已停用", 401)
        return self.user_read(user)

    def user_read(self, user: User) -> AuthUserRead:
        employee = self.repository.get_employee_for_user(user.id)
        return AuthUserRead(
            id=user.id,
            username=user.username,
            role=user.role,
            permissions=normalize_permissions(user.permissions),
            employee_id=employee.id if employee else None,
            full_name=employee.full_name if employee else None,
            department=employee.department if employee else None,
            job_title=employee.job_title if employee else None,
        )

    @staticmethod
    def _verify_password(password: str, password_hash: str) -> bool:
        try:
            return bcrypt.verify(password, password_hash)
        except (ValueError, TypeError):
            return False
