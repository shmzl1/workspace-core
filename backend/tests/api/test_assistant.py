"""Authenticated API contract tests for POST /api/v1/assistant/chat."""

from types import SimpleNamespace
from typing import Any

import pytest
from fastapi.testclient import TestClient

pytest.importorskip("docx", reason="完整 FastAPI 应用导入依赖项目声明的 python-docx")

from app.agents.shared.model_gateway import ModelGatewayInput, ModelGatewayOutput
from app.core.container import get_application_container
from app.core.dependencies import get_current_user
from app.main import app
from app.modules.auth.models import User

client = TestClient(app)


class StaticModelGateway:
    async def generate(self, _request: ModelGatewayInput) -> ModelGatewayOutput:
        return ModelGatewayOutput(structured_output={
            "intent": "CHAT",
            "normalized_query": "用户向智能助手问好",
            "reply": "您好，我可以协助您查询本人假期、薪资考勤影响因素和公司政策。",
            "parameters": {"year": None, "month": None, "policy_keywords": []},
            "updated_summary": "用户刚刚开始与智能助手对话。",
        })


@pytest.fixture(autouse=True)
def clear_dependency_overrides():
    app.dependency_overrides.clear()
    yield
    app.dependency_overrides.clear()


def override_authenticated_dependencies() -> None:
    user = User(id=3, username="assistant-user", role="EMPLOYEE", permissions=[])
    app.dependency_overrides[get_current_user] = lambda: user
    app.dependency_overrides[get_application_container] = lambda: SimpleNamespace(
        model_gateway=StaticModelGateway(),
    )


def test_assistant_chat_requires_authentication() -> None:
    response = client.post(
        "/api/v1/assistant/chat",
        json={"message": "你好", "conversation_summary": "", "recent_messages": []},
        headers={"X-Trace-Id": "assistant-unauthorized"},
    )

    body = response.json()
    assert response.status_code == 401
    assert body["success"] is False
    assert body["error"]["code"] == "TOKEN_INVALID"
    assert body["trace_id"] == "assistant-unauthorized"


def test_assistant_chat_returns_unified_authenticated_response() -> None:
    override_authenticated_dependencies()

    response = client.post(
        "/api/v1/assistant/chat",
        json={
            "message": "你好",
            "conversation_summary": "用户刚开始对话。",
            "recent_messages": [{"role": "user", "content": "你好"}],
        },
        headers={"X-Trace-Id": "assistant-success"},
    )

    body = response.json()
    assert response.status_code == 200
    assert body["success"] is True
    assert body["trace_id"] == "assistant-success"
    assert body["data"]["intent"] == "CHAT"
    assert body["data"]["context"] == {"recent_message_count": 1, "summary_used": True}


@pytest.mark.parametrize(
    "payload",
    [
        {"message": "   "},
        {"message": "问" * 4_001},
        {"message": "你好", "conversation_summary": "摘" * 4_001},
        {"message": "你好", "recent_messages": [{"role": "user", "content": "好"}] * 13},
        {"message": "你好", "recent_messages": [{"role": "system", "content": "好"}]},
        {"message": "你好", "recent_messages": [{"role": "user", "content": "好" * 1_001}]},
    ],
)
def test_assistant_chat_rejects_invalid_input(payload: dict[str, Any]) -> None:
    override_authenticated_dependencies()

    response = client.post("/api/v1/assistant/chat", json=payload)

    assert response.status_code == 422
    assert response.json()["error"]["code"] == "PARAM_VALIDATION_ERROR"
