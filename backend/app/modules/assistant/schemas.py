"""Validated contracts for employee assistant language understanding."""

from enum import Enum
from typing import Annotated, Literal

from pydantic import (
    BaseModel,
    ConfigDict,
    Field,
    StrictFloat,
    StrictInt,
    StringConstraints,
    model_validator,
)


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
FactKey = Annotated[
    str,
    StringConstraints(
        strict=True,
        strip_whitespace=True,
        min_length=1,
        max_length=128,
        pattern=r"^[a-z][a-z0-9_.-]*$",
    ),
]
FactLabel = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=100),
]
FactUnit = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=20),
]
ResultQuerySummary = Annotated[
    str,
    StringConstraints(strip_whitespace=True, min_length=1, max_length=500),
]
CandidateText = Annotated[
    str,
    StringConstraints(strict=True, strip_whitespace=True, min_length=1, max_length=200),
]


class StrictAssistantModel(BaseModel):
    model_config = ConfigDict(extra="forbid")


class AssistantIntent(str, Enum):
    LEAVE = "LEAVE"
    PAYROLL = "PAYROLL"
    POLICY = "POLICY"
    CHAT = "CHAT"
    UNKNOWN = "UNKNOWN"


class AssistantResponseMode(str, Enum):
    QUERY_DATA = "QUERY_DATA"
    ANSWER_FROM_RESULT = "ANSWER_FROM_RESULT"
    CHAT = "CHAT"
    UNKNOWN = "UNKNOWN"


class AssistantResultOperation(str, Enum):
    NONE = "NONE"
    READ = "READ"
    CONFIRM = "CONFIRM"
    COMPARE = "COMPARE"
    EXPLAIN = "EXPLAIN"


class AssistantChatMessage(StrictAssistantModel):
    role: Literal["user", "assistant"]
    content: RecentMessageContent


class AssistantAvailableFact(StrictAssistantModel):
    key: FactKey
    label: FactLabel
    unit: FactUnit | None = None
    value_type: Literal["number", "text", "boolean", "date"]


class AssistantAvailableResultContext(StrictAssistantModel):
    domain: Literal["LEAVE", "PAYROLL", "POLICY"]
    query_summary: ResultQuerySummary
    primary_fact_key: FactKey | None = None
    available_facts: list[AssistantAvailableFact] = Field(min_length=1, max_length=30)

    @model_validator(mode="after")
    def validate_fact_keys(self) -> "AssistantAvailableResultContext":
        fact_keys = [fact.key for fact in self.available_facts]
        if len(fact_keys) != len(set(fact_keys)):
            raise ValueError("available fact keys must be unique")
        if self.primary_fact_key is not None and self.primary_fact_key not in fact_keys:
            raise ValueError("primary fact key must exist in available facts")
        return self


class AssistantChatRequest(StrictAssistantModel):
    message: RequestMessage
    conversation_summary: ConversationSummary = ""
    recent_messages: list[AssistantChatMessage] = Field(default_factory=list, max_length=12)
    available_result_context: AssistantAvailableResultContext | None = None


class AssistantResolvedParameters(StrictAssistantModel):
    year: ResolvedYear | None = None
    month: ResolvedMonth | None = None
    policy_keywords: list[PolicyKeyword] = Field(default_factory=list, max_length=3)


class AssistantContextMetadata(StrictAssistantModel):
    recent_message_count: int = Field(ge=0, le=12)
    summary_used: bool


class AssistantResultReference(StrictAssistantModel):
    operation: AssistantResultOperation = AssistantResultOperation.NONE
    fact_keys: list[FactKey] = Field(default_factory=list, max_length=2)
    candidate_number: StrictInt | StrictFloat | None = None
    candidate_text: CandidateText | None = None


class AssistantChatDecision(StrictAssistantModel):
    """Exact JSON object expected from the shared model gateway."""

    response_mode: AssistantResponseMode
    intent: AssistantIntent
    normalized_query: NormalizedQuery
    reply: AssistantReply
    parameters: AssistantResolvedParameters
    result_reference: AssistantResultReference
    updated_summary: UpdatedSummary


class AssistantChatResponse(AssistantChatDecision):
    context: AssistantContextMetadata
