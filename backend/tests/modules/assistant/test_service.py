"""Tests for the isolated employee AssistantService."""

import asyncio
from copy import deepcopy
from datetime import date
from pathlib import Path
from types import SimpleNamespace
from typing import Any

import pytest
from pydantic import ValidationError

from app.agents.shared.model_errors import (
    ModelGatewayConfigurationError,
    ModelGatewayDisabledError,
    ModelGatewayOutputError,
    ModelGatewayUnavailableError,
)
from app.agents.shared.model_gateway import ModelGatewayInput, ModelGatewayOutput
from app.core.exceptions import TalentFlowError
from app.modules.assistant.schemas import AssistantChatRequest
from app.modules.assistant.service import AssistantService


def valid_output(**overrides: Any) -> dict[str, Any]:
    output: dict[str, Any] = {
        "response_mode": "CHAT",
        "intent": "CHAT",
        "normalized_query": "用户向智能助手问好",
        "reply": "您好，我可以协助您查询本人假期、薪资考勤影响因素和公司政策。",
        "parameters": {"year": None, "month": None, "policy_keywords": []},
        "result_reference": {
            "operation": "NONE",
            "fact_keys": [],
            "candidate_number": None,
            "candidate_text": None,
        },
        "updated_summary": "用户刚刚开始与智能助手对话。",
    }
    output.update(overrides)
    if "response_mode" not in overrides and "intent" in overrides:
        output["response_mode"] = {
            "LEAVE": "QUERY_DATA",
            "PAYROLL": "QUERY_DATA",
            "POLICY": "QUERY_DATA",
            "CHAT": "CHAT",
            "UNKNOWN": "UNKNOWN",
        }.get(str(output["intent"]), "UNKNOWN")
    return output


def available_leave_context() -> dict[str, Any]:
    return {
        "domain": "LEAVE",
        "query_summary": "已查询本人假期余额，可引用额度、已使用和剩余字段。",
        "primary_fact_key": "leave.annual.remaining",
        "available_facts": [
            {
                "key": "leave.annual.total",
                "label": "年假总额度",
                "unit": "天",
                "value_type": "number",
            },
            {
                "key": "leave.annual.used",
                "label": "年假已使用",
                "unit": "天",
                "value_type": "number",
            },
            {
                "key": "leave.annual.remaining",
                "label": "年假当前剩余",
                "unit": "天",
                "value_type": "number",
            },
        ],
    }


class StaticModelGateway:
    def __init__(self, output: Any) -> None:
        self.output = output
        self.requests: list[ModelGatewayInput] = []

    async def generate(self, request: ModelGatewayInput) -> Any:
        self.requests.append(request)
        if isinstance(self.output, dict):
            return ModelGatewayOutput(structured_output=self.output, provider="test", model_name="test")
        return SimpleNamespace(structured_output=self.output)


class RaisingModelGateway:
    def __init__(self, error: Exception) -> None:
        self.error = error

    async def generate(self, _request: ModelGatewayInput) -> ModelGatewayOutput:
        raise self.error


def run_chat(service: AssistantService, payload: AssistantChatRequest):
    return asyncio.run(service.chat(payload))


def test_chat_validates_response_and_sanitizes_model_context() -> None:
    gateway = StaticModelGateway(valid_output())
    service = AssistantService(gateway, today_provider=lambda: date(2026, 7, 16))
    payload = AssistantChatRequest(
        message="你好，我的 Token: abcdef123456",
        conversation_summary="用户工资为 12000 元，Bearer secret-token",
        recent_messages=[
            {"role": "user", "content": "基本工资是 10000 元"},
            {"role": "assistant", "content": "用户 ID: user-123"},
        ],
    )

    result = run_chat(service, payload)

    assert result.intent.value == "CHAT"
    assert result.reply
    assert result.context.recent_message_count == 2
    assert result.context.summary_used is True
    request = gateway.requests[0]
    assert request.task_name == "employee_assistant_understanding"
    assert request.output_schema_name == "AssistantChatDecision"
    assert request.thinking_type == "disabled"
    assert request.max_completion_tokens == 600
    assert request.structured_input["current_date"] == "2026-07-16"
    serialized_context = str(request.structured_input)
    assert "12000" not in serialized_context
    assert "10000" not in serialized_context
    assert "secret-token" not in serialized_context
    assert "user-123" not in serialized_context


@pytest.mark.parametrize(
    ("intent", "parameters", "expected"),
    [
        ("PAYROLL", {"year": 2026, "month": 6, "policy_keywords": []}, (2026, 6, [])),
        ("PAYROLL", {"year": None, "month": None, "policy_keywords": []}, (2026, 7, [])),
        ("LEAVE", {"year": None, "month": 6, "policy_keywords": []}, (2026, None, [])),
        ("POLICY", {"year": 2026, "month": 6, "policy_keywords": ["病假", "病假"]}, (None, None, ["病假"])),
        ("UNKNOWN", {"year": 2026, "month": 6, "policy_keywords": ["年假"]}, (None, None, [])),
    ],
)
def test_business_parameters_are_normalized(
    intent: str,
    parameters: dict[str, Any],
    expected: tuple[int | None, int | None, list[str]],
) -> None:
    gateway = StaticModelGateway(valid_output(intent=intent, parameters=parameters))
    service = AssistantService(gateway, today_provider=lambda: date(2026, 7, 16))

    result = run_chat(service, AssistantChatRequest(message="继续"))

    assert (result.parameters.year, result.parameters.month, result.parameters.policy_keywords) == expected


@pytest.mark.parametrize(
    ("summary", "message", "expected_intent", "expected_parameters"),
    [
        (
            "用户此前查询 2026 年 7 月本人薪资和考勤影响因素。",
            "那上个月呢",
            "PAYROLL",
            {"year": 2026, "month": 6, "policy_keywords": []},
        ),
        (
            "用户此前查询本人年假余额。",
            "病假呢",
            "LEAVE",
            {"year": 2026, "month": None, "policy_keywords": []},
        ),
        (
            "用户正在询问年假结转政策。",
            "那病假呢",
            "POLICY",
            {"year": None, "month": None, "policy_keywords": ["病假"]},
        ),
    ],
)
def test_contextual_follow_up_contracts(
    summary: str,
    message: str,
    expected_intent: str,
    expected_parameters: dict[str, Any],
) -> None:
    gateway = StaticModelGateway(valid_output(
        intent=expected_intent,
        normalized_query=message,
        parameters=expected_parameters,
    ))
    service = AssistantService(gateway, today_provider=lambda: date(2026, 7, 16))

    result = run_chat(service, AssistantChatRequest(message=message, conversation_summary=summary))

    assert result.intent.value == expected_intent
    assert result.parameters.model_dump() == expected_parameters


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "   "},
        {"message": "问" * 4_001},
        {"message": "你好", "conversation_summary": "摘" * 4_001},
        {
            "message": "你好",
            "recent_messages": [{"role": "user", "content": "你好"}] * 13,
        },
        {"message": "你好", "recent_messages": [{"role": "system", "content": "你好"}]},
        {"message": "你好", "recent_messages": [{"role": "user", "content": "问" * 1_001}]},
    ],
)
def test_request_schema_rejects_invalid_or_unbounded_context(payload: dict[str, Any]) -> None:
    with pytest.raises(ValidationError):
        AssistantChatRequest.model_validate(payload)


def test_available_result_context_validates_without_business_values() -> None:
    payload = AssistantChatRequest.model_validate({
        "message": "是 11 天吗",
        "available_result_context": available_leave_context(),
    })

    assert payload.available_result_context is not None
    assert payload.available_result_context.primary_fact_key == "leave.annual.remaining"
    assert not hasattr(payload.available_result_context.available_facts[0], "value")


def test_available_result_context_rejects_value_field() -> None:
    context = available_leave_context()
    context["available_facts"][2]["value"] = 11

    with pytest.raises(ValidationError):
        AssistantChatRequest.model_validate({
            "message": "是 11 天吗",
            "available_result_context": context,
        })


def result_answer_output(**reference_overrides: Any) -> dict[str, Any]:
    reference = {
        "operation": "CONFIRM",
        "fact_keys": ["leave.annual.remaining"],
        "candidate_number": 11,
        "candidate_text": None,
    }
    reference.update(reference_overrides)
    return valid_output(
        response_mode="ANSWER_FROM_RESULT",
        intent="LEAVE",
        normalized_query="确认上一轮年假当前剩余是否与用户候选值一致",
        reply="正在根据上一轮真实结果进行确认。",
        parameters={"year": None, "month": None, "policy_keywords": []},
        result_reference=reference,
        updated_summary="用户正在确认上一轮本人年假余额结果。",
    )


def test_result_confirmation_uses_only_available_fact_descriptions() -> None:
    gateway = StaticModelGateway(result_answer_output())
    service = AssistantService(gateway, today_provider=lambda: date(2026, 7, 16))
    payload = AssistantChatRequest.model_validate({
        "message": "是 11 天吗",
        "available_result_context": available_leave_context(),
    })

    result = run_chat(service, payload)

    assert result.response_mode.value == "ANSWER_FROM_RESULT"
    assert result.result_reference.operation.value == "CONFIRM"
    assert result.result_reference.candidate_number == 11
    sent_context = gateway.requests[0].structured_input["available_result_context"]
    assert sent_context == available_leave_context()
    assert all("value" not in fact for fact in sent_context["available_facts"])


def test_result_confirmation_canonicalizes_non_authoritative_model_text() -> None:
    output = result_answer_output()
    output["reply"] = "是的，年假当前剩余 11 天。"
    output["updated_summary"] = "用户正在确认年假当前剩余是否为 11 天。"
    service = AssistantService(StaticModelGateway(output))
    payload = AssistantChatRequest.model_validate({
        "message": "是11天吗？",
        "available_result_context": available_leave_context(),
    })

    result = run_chat(service, payload)

    assert result.response_mode.value == "ANSWER_FROM_RESULT"
    assert result.reply == "正在根据上一轮真实结果进行确认。"
    assert result.updated_summary == "用户正在确认上一轮本人假期结果。"
    assert "11" not in result.reply
    assert "11" not in result.updated_summary


@pytest.mark.parametrize(
    "output",
    [
        result_answer_output(fact_keys=["leave.fake.remaining"]),
        result_answer_output(fact_keys=[]),
        result_answer_output(operation="COMPARE", fact_keys=["leave.annual.remaining"]),
        result_answer_output(candidate_number=None, candidate_text=None),
        valid_output(
            response_mode="QUERY_DATA",
            intent="LEAVE",
            result_reference={
                "operation": "NONE",
                "fact_keys": ["leave.annual.remaining"],
                "candidate_number": None,
                "candidate_text": None,
            },
        ),
    ],
)
def test_invalid_result_reference_contracts_are_rejected(output: dict[str, Any]) -> None:
    service = AssistantService(StaticModelGateway(output))
    payload = AssistantChatRequest.model_validate({
        "message": "继续",
        "available_result_context": available_leave_context(),
    })

    with pytest.raises(TalentFlowError) as raised:
        run_chat(service, payload)

    assert raised.value.code == "ASSISTANT_MODEL_OUTPUT_INVALID"


def test_result_answer_requires_available_context() -> None:
    service = AssistantService(StaticModelGateway(result_answer_output()))

    with pytest.raises(TalentFlowError) as raised:
        run_chat(service, AssistantChatRequest(message="是 11 天吗"))

    assert raised.value.code == "ASSISTANT_MODEL_OUTPUT_INVALID"


def test_first_leave_request_remains_query_data() -> None:
    gateway = StaticModelGateway(valid_output(
        response_mode="QUERY_DATA",
        intent="LEAVE",
        normalized_query="查询本人假期余额",
        reply="好的，我将查询您的假期余额。",
        parameters={"year": 2026, "month": None, "policy_keywords": []},
    ))

    result = run_chat(
        AssistantService(gateway, today_provider=lambda: date(2026, 7, 16)),
        AssistantChatRequest(message="假期还剩多少天"),
    )

    assert result.response_mode.value == "QUERY_DATA"
    assert result.intent.value == "LEAVE"
    assert result.result_reference.operation.value == "NONE"


def invalid_output_cases() -> list[Any]:
    cases: list[Any] = ["not-json", [valid_output()]]
    illegal_intent = valid_output(intent="OTHER")
    missing_reply = valid_output()
    missing_reply.pop("reply")
    illegal_month = valid_output(parameters={"year": 2026, "month": 13, "policy_keywords": []})
    illegal_year = valid_output(parameters={"year": 1999, "month": 6, "policy_keywords": []})
    wrong_keywords = valid_output(parameters={"year": None, "month": None, "policy_keywords": "年假"})
    too_many_keywords = valid_output(parameters={
        "year": None,
        "month": None,
        "policy_keywords": ["一", "二", "三", "四"],
    })
    long_summary = valid_output(updated_summary="摘" * 4_001)
    sensitive_summary = valid_output(updated_summary="用户实发工资为 12000 元。")
    arbitrary_route = valid_output(reply="请调用 /api/v1/payroll/me")
    extra_field = valid_output(tool_name="salary_lookup")
    cases.extend([
        illegal_intent,
        missing_reply,
        illegal_month,
        illegal_year,
        wrong_keywords,
        too_many_keywords,
        long_summary,
        sensitive_summary,
        arbitrary_route,
        extra_field,
    ])
    return cases


@pytest.mark.parametrize("output", invalid_output_cases())
def test_invalid_model_output_is_rejected_without_leaking_content(output: Any) -> None:
    service = AssistantService(StaticModelGateway(deepcopy(output)))

    with pytest.raises(TalentFlowError) as raised:
        run_chat(service, AssistantChatRequest(message="你好"))

    assert raised.value.code == "ASSISTANT_MODEL_OUTPUT_INVALID"
    assert raised.value.status_code == 502
    assert "/api/" not in raised.value.message
    assert "12000" not in raised.value.message


@pytest.mark.parametrize(
    ("error", "code"),
    [
        (ModelGatewayDisabledError("internal disabled detail"), "ASSISTANT_MODEL_DISABLED"),
        (ModelGatewayConfigurationError("secret model url"), "ASSISTANT_MODEL_MISCONFIGURED"),
        (ModelGatewayUnavailableError("proxy=http://secret"), "ASSISTANT_MODEL_UNAVAILABLE"),
        (ModelGatewayOutputError("raw model response"), "ASSISTANT_MODEL_OUTPUT_INVALID"),
    ],
)
def test_model_errors_are_mapped_to_safe_business_errors(error: Exception, code: str) -> None:
    service = AssistantService(RaisingModelGateway(error))

    with pytest.raises(TalentFlowError) as raised:
        run_chat(service, AssistantChatRequest(message="你好"))

    assert raised.value.code == code
    assert "secret" not in raised.value.message
    assert "proxy" not in raised.value.message
    assert "raw model" not in raised.value.message


def test_assistant_service_is_isolated_from_recruitment_runtime_and_repositories() -> None:
    service_path = Path(__file__).resolve().parents[3] / "app" / "modules" / "assistant" / "service.py"
    source = service_path.read_text(encoding="utf-8")

    for forbidden_import in (
        "app.agents.runtime",
        "app.agents.workflows",
        "app.agents.tools",
        "app.modules.agent_runtime",
        "Repository",
        "AgentRunStore",
        "AgentEvent",
        "SSE",
    ):
        assert forbidden_import not in source
