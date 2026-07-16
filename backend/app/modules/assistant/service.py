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
    AssistantAvailableResultContext,
    AssistantChatDecision,
    AssistantChatRequest,
    AssistantChatResponse,
    AssistantContextMetadata,
    AssistantIntent,
    AssistantResponseMode,
    AssistantResolvedParameters,
    AssistantResultOperation,
)

_SUPPORTED_INTENTS = [intent.value for intent in AssistantIntent]
_SUPPORTED_RESPONSE_MODES = [mode.value for mode in AssistantResponseMode]
_SUPPORTED_RESULT_OPERATIONS = [operation.value for operation in AssistantResultOperation]
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
_RESULT_VALUE_PATTERN = re.compile(
    r"\d+(?:\.\d+)?\s*(?:天|小时|元|人民币|CNY|RMB|次)",
    flags=re.IGNORECASE,
)
_NON_NEUTRAL_REPLY_PATTERN = re.compile(r"^\s*(?:是的|不是|对的|不对)")


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
            "available_result_context": _available_result_context_input(
                payload.available_result_context
            ),
            "supported_intents": _SUPPORTED_INTENTS,
            "supported_response_modes": _SUPPORTED_RESPONSE_MODES,
            "supported_result_operations": _SUPPORTED_RESULT_OPERATIONS,
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
            _validate_forbidden_model_output(decision)
            _validate_decision_contract(decision, payload.available_result_context)
            decision = _canonicalize_result_answer_text(decision)
            _validate_safe_model_output(decision)
            parameters = _normalize_parameters(decision, current_date)
        except (AttributeError, TypeError, ValidationError, ValueError) as exc:
            raise _invalid_output_error() from exc

        return AssistantChatResponse(
            response_mode=decision.response_mode,
            intent=decision.intent,
            normalized_query=decision.normalized_query,
            reply=decision.reply,
            parameters=parameters,
            result_reference=decision.result_reference,
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
    if decision.response_mode is not AssistantResponseMode.QUERY_DATA:
        return AssistantResolvedParameters()
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


def _available_result_context_input(
    context: AssistantAvailableResultContext | None,
) -> dict[str, Any] | None:
    if context is None:
        return None
    return {
        "domain": context.domain,
        "query_summary": _sanitize_context_text(context.query_summary, 500),
        "primary_fact_key": context.primary_fact_key,
        "available_facts": [
            {
                "key": fact.key,
                "label": _sanitize_context_text(fact.label, 100),
                "unit": _sanitize_context_text(fact.unit, 20) if fact.unit else None,
                "value_type": fact.value_type,
            }
            for fact in context.available_facts
        ],
    }


def _model_output_texts(decision: AssistantChatDecision) -> tuple[str, ...]:
    return (
        decision.normalized_query,
        decision.reply,
        decision.updated_summary,
        decision.result_reference.candidate_text or "",
        *decision.parameters.policy_keywords,
    )


def _validate_forbidden_model_output(decision: AssistantChatDecision) -> None:
    output_texts = _model_output_texts(decision)
    if any(_FORBIDDEN_OUTPUT_PATTERN.search(text) for text in output_texts):
        raise ValueError("model output contains a forbidden route or tool reference")
    if any(pattern.search(text) for pattern in _SENSITIVE_TEXT_PATTERNS for text in output_texts):
        raise ValueError("model output contains sensitive data")


def _canonicalize_result_answer_text(
    decision: AssistantChatDecision,
) -> AssistantChatDecision:
    if decision.response_mode is not AssistantResponseMode.ANSWER_FROM_RESULT:
        return decision

    operation_text = {
        AssistantResultOperation.READ: ("读取", "正在读取上一轮真实结果。"),
        AssistantResultOperation.CONFIRM: ("确认", "正在根据上一轮真实结果进行确认。"),
        AssistantResultOperation.COMPARE: ("比较", "正在比较上一轮真实结果。"),
        AssistantResultOperation.EXPLAIN: ("解释", "正在根据上一轮真实结果进行解释。"),
    }.get(decision.result_reference.operation, ("处理", "正在处理上一轮真实结果。"))
    intent_label = {
        AssistantIntent.LEAVE: "假期",
        AssistantIntent.PAYROLL: "薪资与考勤",
        AssistantIntent.POLICY: "政策",
    }.get(decision.intent, "业务")
    action, reply = operation_text
    return decision.model_copy(
        update={
            "reply": reply,
            "updated_summary": f"用户正在{action}上一轮本人{intent_label}结果。",
        }
    )


def _validate_safe_model_output(decision: AssistantChatDecision) -> None:
    _validate_forbidden_model_output(decision)
    if _RESULT_VALUE_PATTERN.search(decision.updated_summary):
        raise ValueError("updated summary contains a business result value")
    if (
        decision.response_mode is AssistantResponseMode.ANSWER_FROM_RESULT
        and (
            _RESULT_VALUE_PATTERN.search(decision.reply)
            or _NON_NEUTRAL_REPLY_PATTERN.search(decision.reply)
            or any(character.isdigit() for character in decision.updated_summary)
        )
    ):
        raise ValueError("result-answer text contains a business result value")


def _validate_decision_contract(
    decision: AssistantChatDecision,
    available_context: AssistantAvailableResultContext | None,
) -> None:
    reference = decision.result_reference
    has_candidate = (
        reference.candidate_number is not None or reference.candidate_text is not None
    )

    if decision.response_mode is AssistantResponseMode.ANSWER_FROM_RESULT:
        if available_context is None:
            raise ValueError("result answer requires available result context")
        if decision.intent.value != available_context.domain:
            raise ValueError("result answer intent does not match available result domain")
        if reference.operation is AssistantResultOperation.NONE:
            raise ValueError("result answer requires an operation")

        available_keys = {fact.key for fact in available_context.available_facts}
        if not reference.fact_keys or any(
            key not in available_keys for key in reference.fact_keys
        ):
            raise ValueError("result answer references an unavailable fact")
        if len(reference.fact_keys) != len(set(reference.fact_keys)):
            raise ValueError("result answer fact keys must be unique")

        if reference.operation is AssistantResultOperation.CONFIRM and not has_candidate:
            raise ValueError("confirmation requires a candidate value")
        if (
            reference.operation is AssistantResultOperation.COMPARE
            and len(reference.fact_keys) != 2
        ):
            raise ValueError("comparison requires exactly two facts")
        if (
            reference.operation in {
                AssistantResultOperation.READ,
                AssistantResultOperation.EXPLAIN,
            }
            and len(reference.fact_keys) < 1
        ):
            raise ValueError("read or explanation requires a fact")
        return

    if (
        reference.operation is not AssistantResultOperation.NONE
        or reference.fact_keys
        or has_candidate
    ):
        raise ValueError("non-result response cannot reference result facts")

    if decision.response_mode is AssistantResponseMode.QUERY_DATA:
        if decision.intent not in {
            AssistantIntent.LEAVE,
            AssistantIntent.PAYROLL,
            AssistantIntent.POLICY,
        }:
            raise ValueError("data query requires a business intent")
    elif decision.response_mode is AssistantResponseMode.CHAT:
        if decision.intent is not AssistantIntent.CHAT:
            raise ValueError("chat mode requires CHAT intent")
    elif decision.response_mode is AssistantResponseMode.UNKNOWN:
        if decision.intent is not AssistantIntent.UNKNOWN:
            raise ValueError("unknown mode requires UNKNOWN intent")


def _invalid_output_error() -> TalentFlowError:
    return TalentFlowError(
        "ASSISTANT_MODEL_OUTPUT_INVALID",
        "智能理解服务返回了无法安全处理的内容，请重新表述后再试。",
        502,
    )
