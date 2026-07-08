"""Authentication route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import current_identity
from app.core.security import DemoIdentity
from app.modules.auth.service import AuthService
from app.shared.response import ok

router = APIRouter()


def get_auth_service(session: Session = Depends(get_db_session)) -> AuthService:
    return AuthService.from_session(session)


@router.get("/me")
def me(
    identity: DemoIdentity = Depends(current_identity),
    service: AuthService = Depends(get_auth_service),
) -> object:
    return ok(service.current_context(identity))


@router.get("/demo-users")
def demo_users(service: AuthService = Depends(get_auth_service)) -> object:
    return ok(service.list_demo_users())
