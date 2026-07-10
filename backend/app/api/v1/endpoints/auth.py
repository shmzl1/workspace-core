"""Authentication route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import get_current_user
from app.modules.auth.models import User
from app.modules.auth.schemas import LoginRequest
from app.modules.auth.service import AuthService
from app.shared.response import ok

router = APIRouter()


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService.from_session(session)


@router.post("/login")
def login(payload: LoginRequest, service: AuthService = Depends(get_auth_service)) -> object:
    return ok(service.login(payload.username, payload.password))


@router.get("/me")
def me(
    current_user: User = Depends(get_current_user),
    service: AuthService = Depends(get_auth_service),
) -> object:
    return ok(service.get_current_user(current_user))
