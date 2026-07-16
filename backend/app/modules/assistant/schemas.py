"""Validated contracts for employee assistant language understanding."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import BaseModel, ConfigDict, Field, StringConstraints


RequestMessage = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=4_000),
]
ConversationSummary = Annotated[
    str,
    StringConstraints(strip_whitespace=True, max_length=4_000),
]
RecentMessageContent = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=1_000),
]
NormalizedQuery = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=1_000),
]
AssistantReply = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=2_000),
]
UpdatedSummary = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, max_length=4_000),
]
PolicyKeyword = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=32),
]
ResolvedYear = Annotated[int, Field(strict=True, ge=2_000, le=2_100)]
ResolvedMonth = Annotated[int, Field(strict=True, ge=1, le=12)]


class StrictAssistantModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssistantIntent(str, Enum):
    LEAVE = "LEAVE"
    PAYROLL = "PAYROLL"
    POLICY = "POLICY"
    CHAT = "CHAT"
    UNKNOWN = "UNKNOWN"


class AssistantChatMessage(StrictAssistantModel):
    role: Literal["user", "assistant"]
    content: RecentMessageContent


class AssistantChatRequest(StrictAssistantModel):
    message: RequestMessage
    conversation_summary: ConversationSummary = ""
    recent_messages: list[AssistantChatMessage] = Field(default_factory=list, max_length=12)


class AssistantResolvedParameters(StrictAssistantModel):
    year: ResolvedYear | None = None
    month: ResolvedMonth | None = None
    policy_keywords: list[PolicyKeyword] = Field(default_factory=list, max_length=3)


class AssistantContextMetadata(StrictAssistantModel):
    recent_message_count: int = Field(ge=0, le=12)
    summary_used: bool


class AssistantChatDecision(StrictAssistantModel):
    """Exact JSON object expected from the shared model gateway."""

    intent: AssistantIntent
    normalized_query: NormalizedQuery
    reply: AssistantReply
    parameters: AssistantResolvedParameters
    updated_summary: UpdatedSummary


class AssistantChatResponse(AssistantChatDecision):
    context: AssistantContextMetadata
