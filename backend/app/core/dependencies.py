"""Shared FastAPI dependencies."""

# pyrefly: ignore [missing-import]
from fastapi import Depends, Header, HTTPException, status
# pyrefly: ignore [missing-import]
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
# pyrefly: ignore [missing-import]
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.database import get_db_session
from app.core.exceptions import TalentFlowError
from app.core.security import DemoIdentity, parse_demo_identity
from app.modules.auth.models import User
from app.modules.employee.models import Employee
from app.shared.trace import set_trace_id

security = HTTPBearer(auto_error=False)


def trace_context(x_trace_id: str | None = Header(default=None, alias="X-Trace-Id")) -> str:
    return set_trace_id(x_trace_id)


def get_current_user(
    credentials: HTTPAuthorizationCredentials | None = Depends(security),
    x_mock_user_id: int | None = Header(default=None, alias="X-Mock-User-Id"),
    x_mock_role: str | None = Header(default=None, alias="X-Mock-Role"),
    db: Session = Depends(get_db_session),
) -> User:
    """Retrieve the current user from JWT or mock headers for dev/test."""
    if x_mock_user_id is not None:
        user = db.query(User).filter(User.id == x_mock_user_id).first()
        if user and user.is_active:
            if x_mock_role and x_mock_role != user.role:
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mock identity role mismatch")
            return user
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Mock identity is invalid")

    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Not authenticated",
        )

    token = credentials.credentials
    settings = get_settings()
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=[settings.jwt_algorithm])
        username: str | None = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid token payload")
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")

    user = db.query(User).filter(User.username == username).first()
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="User not found")
    return user


def get_current_employee(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db_session),
) -> Employee:
    """Retrieve the Employee linked to the current logged-in user."""
    employee = db.query(Employee).filter(Employee.user_id == current_user.id).first()
    if not employee:
        raise TalentFlowError("EMPLOYEE_NOT_FOUND", "当前用户没有关联的员工档案")
    return employee


def current_identity(x_demo_identity: str | None = Header(default=None, alias="X-Demo-Identity")) -> DemoIdentity:
    return parse_demo_identity(x_demo_identity)
