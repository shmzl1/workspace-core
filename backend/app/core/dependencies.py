"""Shared FastAPI authentication and permission dependencies."""

from collections.abc import Callable

from fastapi import Depends, Header
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import ExpiredSignatureError, JWTError, jwt
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.exceptions import TalentFlowError
from app.modules.auth.models import User
from app.modules.auth.permissions import normalize_permissions
from app.modules.employee.models import Employee
from app.shared.trace import set_trace_id

security = HTTPBearer(auto_error=False)


def trace_context(x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")) -> str:
    return set_trace_id(x_trace_id)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    db: Session = Depends(get_db_session),
) -> User:
    if credentials is None or credentials.scheme.lower() != "bearer":
        raise TalentFlowError("TOKEN_INVALID", "未提供有效登录凭证。", 401)
    settings = get_settings()
    try:
        payload = jwt.decode(credentials.credentials, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
    except ExpiredSignatureError as exc:
        raise TalentFlowError("TOKEN_EXPIRED", "登录状态已过期，请重新登录。", 401) from exc
    except JWTError as exc:
        raise TalentFlowError("TOKEN_INVALID", "登录凭证无效。", 401) from exc
    user_id = payload.get("user_id")
    username = payload.get("sub")
    if not isinstance(user_id, int) or not isinstance(username, str):
        raise TalentFlowError("TOKEN_INVALID", "登录凭证无效。", 401)
    user = db.get(User, user_id)
    if user is None or user.username != username:
        raise TalentFlowError("TOKEN_INVALID", "登录账号不存在。", 401)
    if not user.is_active:
        raise TalentFlowError("USER_INACTIVE", "账号已停用。", 401)
    return user


def get_current_employee(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Employee:
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise TalentFlowError("EMPLOYEE_NOT_FOUND", "当前用户没有关联的员工档案。")
    return employee


def user_permissions(user: User) -> set[str]:
    return set(normalize_permissions(user.permissions))


def require_permission(permission: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if permission not in user_permissions(current_user):
            raise TalentFlowError("PERMISSION_DENIED", "当前账号没有执行此操作的权限。", 403)
        return current_user
    return dependency


def require_any_permission(*permissions: str) -> Callable:
    def dependency(current_user: User = Depends(get_current_user)) -> User:
        if not user_permissions(current_user).intersection(permissions):
            raise TalentFlowError("PERMISSION_DENIED", "当前账号没有执行此操作的权限。", 403)
        return current_user
    return dependency
