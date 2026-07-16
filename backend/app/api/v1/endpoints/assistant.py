"""Authenticated route boundary for employee assistant language understanding."""

from fastapi import APIRouter, Depends

from app.core.container import ApplicationContainer, get_application_container
from app.core.dependencies import get_current_user
from app.modules.assistant.schemas import AssistantChatRequest, AssistantChatResponse
from app.modules.assistant.service import AssistantService
from app.modules.auth.models import User
from app.shared.response import ApiResponse, ok

router = APIRouter()


@router.post("/chat", response_model=ApiResponse[AssistantChatResponse])
async def chat(
    payload: AssistantChatRequest,
    _current_user: User = Depends(get_current_user),
    container: ApplicationContainer = Depends(get_application_container),
) -> ApiResponse[AssistantChatResponse]:
    """Resolve language intent only; business data stays in existing APIs."""

    service = AssistantService(container.model_gateway)
    return ok(await service.chat(payload))
