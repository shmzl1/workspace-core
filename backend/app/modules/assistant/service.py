"""Isolated language-understanding service for the employee assistant."""

import re
from collections.abc import Callable
from datetime import date
from typing import Any

from pydantic import ValidationError

from app.agents.shared.model_errors import (
    ModelGatewayConfigurationError,
    ModelGatewayDisabledError,
    ModelGatewayOutputError,
    ModelGatewayUnavailableError,
)
from app.agents.shared.model_gateway import ModelGateway, ModelGatewayInput
from app.core.exceptions import TalentFlowError
from app.modules.assistant.prompts import ASSISTANT_SYSTEM_PROMPT
from app.modules.assistant.schemas import (
    AssistantChatDecision,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantContextMetadata,
    AssistantIntent,
    AssistantResolvedParameters,
)

_SUPPORTED_INTENTS = [intent.value for intent in AssistantIntent]
_FORBIDDEN_OUTPUT_PATTERN = re.compile(
    r"https?://|/api(?:/|\b)|\btool_calls?\b|工具调用|接口地址",
    flags=re.IGNORECASE,
)
_SENSITIVE_TEXT_PATTERNS = (
    re.compile(r"\bBearer\s+[A-Za-z0-9._~+/=-]+", flags=re.IGNORECASE),
    re.compile(
        r"(?:api[_ -]?key|token|密码|password|员工编号|employee[_ -]?id|用户\s*id|user[_ -]?id)"
        r"\s*[:：=]?\s*[A-Za-z0-9._~+/=-]{3,}",
        flags=re.IGNORECASE,
    ),
    re.compile(
        r"(?:实发工资|基本工资|绩效工资|扣款|工资|薪资|金额)"
        r"[^\n，。；]{0,12}\d+(?:\.\d+)?\s*(?:元|人民币|CNY|RMB)",
        flags=re.IGNORECASE,
    ),
)
_REDACTION_RULES = (
    (_SENSITIVE_TEXT_PATTERNS[0], "[已脱敏凭证]"),
    (_SENSITIVE_TEXT_PATTERNS[1], "[已脱敏敏感字段]"),
    (_SENSITIVE_TEXT_PATTERNS[2], "[已脱敏薪资金额]"),
)


class AssistantService:
    """Use the shared ModelGateway without touching Agent Runtime or business data."""

    def __init__(
        self,
        model_gateway: ModelGateway,
        *,
        today_provider: Callable[[], date] = date.today,
    ) -> None:
        self._model_gateway = model_gateway
        self._today_provider = today_provider

    async def chat(self, payload: AssistantChatRequest) -> AssistantChatResponse:
        current_date = self._today_provider()
        structured_input = {
            "current_date": current_date.isoformat(),
            "message": _sanitize_context_text(payload.message, 4_000),
            "conversation_summary": _sanitize_context_text(
                payload.conversation_summary,
                4_000,
            ),
            "recent_messages": [
                {
                    "role": message.role,
                    "content": _sanitize_context_text(message.content, 1_000),
                }
                for message in payload.recent_messages[-12:]
            ],
            "supported_intents": _SUPPORTED_INTENTS,
        }
        try:
            gateway_output = await self._model_gateway.generate(
                ModelGatewayInput(
                    task_name="employee_assistant_understanding",
                    system_context={"prompt": ASSISTANT_SYSTEM_PROMPT},
                    structured_input=structured_input,
                    output_schema_name="AssistantChatDecision",
                    thinking_type="disabled",
                    max_completion_tokens=600,
                )
            )
        except ModelGatewayDisabledError as exc:
            raise TalentFlowError(
                "ASSISTANT_MODEL_DISABLED",
                "智能理解服务当前未启用，请使用支持的业务关键词重试。",
                503,
            ) from exc
        except ModelGatewayConfigurationError as exc:
            raise TalentFlowError(
                "ASSISTANT_MODEL_MISCONFIGURED",
                "智能理解服务当前配置不完整，请稍后重试。",
                503,
            ) from exc
        except ModelGatewayUnavailableError as exc:
            raise TalentFlowError(
                "ASSISTANT_MODEL_UNAVAILABLE",
                "智能理解服务当前不可用，请稍后重试。",
                503,
            ) from exc
        except ModelGatewayOutputError as exc:
            raise _invalid_output_error() from exc
        except Exception as exc:
            raise TalentFlowError(
                "ASSISTANT_MODEL_UNAVAILABLE",
                "智能理解服务当前不可用，请稍后重试。",
                503,
            ) from exc

        try:
            raw_output: Any = gateway_output.structured_output
            decision = AssistantChatDecision.model_validate(raw_output)
            _validate_safe_model_output(decision)
            parameters = _normalize_parameters(decision, current_date)
        except (AttributeError, TypeError, ValidationError, ValueError) as exc:
            raise _invalid_output_error() from exc

        return AssistantChatResponse(
            intent=decision.intent,
            normalized_query=decision.normalized_query,
            reply=decision.reply,
            parameters=parameters,
            updated_summary=decision.updated_summary,
            context=AssistantContextMetadata(
                recent_message_count=len(payload.recent_messages),
                summary_used=bool(payload.conversation_summary),
            ),
        )


def _normalize_parameters(
    decision: AssistantChatDecision,
    current_date: date,
) -> AssistantResolvedParameters:
    parameters = decision.parameters
    if decision.intent is AssistantIntent.PAYROLL:
        return AssistantResolvedParameters(
            year=parameters.year or current_date.year,
            month=parameters.month or current_date.month,
        )
    if decision.intent is AssistantIntent.LEAVE:
        return AssistantResolvedParameters(year=parameters.year or current_date.year)
    if decision.intent is AssistantIntent.POLICY:
        unique_keywords: list[str] = []
        for keyword in parameters.policy_keywords:
            if keyword not in unique_keywords:
                unique_keywords.append(keyword)
        return AssistantResolvedParameters(policy_keywords=unique_keywords)
    return AssistantResolvedParameters()


def _sanitize_context_text(value: str, max_length: int) -> str:
    sanitized = value.strip()
    for pattern, replacement in _REDACTION_RULES:
        sanitized = pattern.sub(replacement, sanitized)
    return sanitized[:max_length]


def _validate_safe_model_output(decision: AssistantChatDecision) -> None:
    output_texts = (
        decision.normalized_query,
        decision.reply,
        decision.updated_summary,
        *decision.parameters.policy_keywords,
    )
    if any(_FORBIDDEN_OUTPUT_PATTERN.search(text) for text in output_texts):
        raise ValueError("model output contains a forbidden route or tool reference")
    if any(pattern.search(text) for pattern in _SENSITIVE_TEXT_PATTERNS for text in output_texts):
        raise ValueError("model output contains sensitive data")


def _invalid_output_error() -> TalentFlowError:
    return TalentFlowError(
        "ASSISTANT_MODEL_OUTPUT_INVALID",
        "智能理解服务返回了无法安全处理的内容，请重新表述后再试。",
        502,
    )
