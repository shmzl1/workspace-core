"""Policy route boundary."""

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.core.database import get_db_session
from app.core.dependencies import require_permission
from app.modules.policy.service import PolicyService
from app.shared.response import ok

router = APIRouter()


@router.get("")
def list_policy_documents(
    query: str | None = None,
    _=Depends(require_permission("policy.read")),
    session: Session = Depends(get_db_session),
) -> object:
    return ok(PolicyService(session).overview(query))
