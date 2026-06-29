import json
from dataclasses import dataclass, field

import pytest

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMResponse


@dataclass
class VerdictGateway:
    calls: list[tuple[str, dict | None]] = field(default_factory=list)

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, response_format))
        if response_format is None:
            content = f"Предварительное мнение {agent.code}"
        else:
            content = json.dumps(
                {
                    "type": "verdict",
                    "lawyer_id": "lawyer_2",
                    "jurisdiction": "UZ",
                    "short_conclusion": "Структурированный вывод",
                    "facts_established": ["Факт подтвержден"],
                    "facts_missing": [],
                    "legal_sources": [],
                    "analysis": ["Нужна дальнейшая проверка источников"],
                    "risks": ["Источник пока не связан"],
                    "recommended_actions": ["Проверить источник"],
                    "confidence": "medium",
                    "confirmed_in_context": True,
                    "source_check_status": "confirmed",
                    "document_generation_allowed": True,
                    "approval_required": "none",
                },
                ensure_ascii=False,
            )
        return LLMResponse(
            content=content,
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=10,
            output_tokens=20,
        )


def _chat_with_user_message(client, content: str) -> int:
    chat_id = client.post("/api/chats", json={"title": "Verdict mode"}).json()["id"]
    response = client.post(f"/api/chats/{chat_id}/messages", json={"content": content})
    assert response.status_code == 201
    return chat_id


def test_lawyer_1_cannot_invoke_verdict_mode(client) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "Оформи вердикт")

    response = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": "lawyer_1", "mode": "verdict"},
    )

    assert response.status_code == 400
    assert "Lawyer 1 cannot issue verdict" in response.json()["detail"]
    assert gateway.calls == []


@pytest.mark.parametrize("agent_code", ["lawyer_2", "lawyer_3"])
def test_eligible_lawyer_creates_conservative_structured_verdict_with_permission(client, agent_code: str) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "Подготовь финальный вывод")

    response = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": agent_code, "mode": "verdict"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_verdict"] is True
    assert body["structured_payload"]["type"] == "verdict"
    assert body["structured_payload"]["lawyer_id"] == agent_code
    assert body["source_check_status"] == "unconfirmed"
    assert body["document_generation_allowed"] is False
    assert body["approval_required"] is None
    for field in (
        "confirmed_in_context",
        "source_check_status",
        "document_generation_allowed",
        "approval_required",
    ):
        assert field not in body["structured_payload"]
    assert gateway.calls == [(agent_code, {"type": "json_object"})]
    assert client.get(f"/api/chats/{chat_id}").json()["active_verdict_message_id"] == body["id"]


def test_lawyer_2_accepts_explicit_own_verdict_phrase(client) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "ок. оформи свой вердикт тогда!")

    response = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": "lawyer_2", "mode": "verdict"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["is_verdict"] is True
    assert body["structured_payload"]["type"] == "verdict"
    assert body["source_check_status"] == "unconfirmed"
    assert body["document_generation_allowed"] is False
    assert gateway.calls == [("lawyer_2", {"type": "json_object"})]


@pytest.mark.parametrize("content", ["понятно", "согласен", "ок", "ну да", "в принципе ясно", "проверь вопрос"])
def test_missing_or_ambiguous_permission_returns_plain_clarification(client, content: str) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, content)

    response = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": "lawyer_2", "mode": "verdict"},
    )

    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Подготовить финальный вердикт?"
    assert body["structured_payload"] is None
    assert body["is_verdict"] is False
    assert body["document_generation_allowed"] is False
    assert gateway.calls == []
    assert client.get(f"/api/chats/{chat_id}").json()["active_verdict_message_id"] is None


def test_normal_mode_remains_non_verdict_even_when_text_mentions_verdict(client) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "Оформи вердикт")

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 200
    body = response.json()
    assert body["content"].startswith("Предварительное мнение")
    assert body["structured_payload"] is None
    assert body["is_verdict"] is False
    assert gateway.calls == [("lawyer_2", None)]


def test_unconfirmed_verdict_cannot_generate_document(client) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "Дай финальное заключение")
    verdict = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": "lawyer_2", "mode": "verdict"},
    )
    assert verdict.status_code == 200

    generated = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={"agent_code": "lawyer_2", "document_type": "claim_letter", "title": "Письмо"},
    )

    assert generated.status_code == 400
    assert generated.json()["detail"] == "Verdict is not verified for document generation."


@pytest.mark.parametrize("agent_code", ["lawyer_1", "lawyer_2"])
def test_normal_agent_message_cannot_be_manually_marked_as_verdict(client, agent_code: str) -> None:
    gateway = VerdictGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = _chat_with_user_message(client, "Предварительный вопрос")
    normal = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": agent_code}).json()

    response = client.post(f"/api/chats/{chat_id}/messages/{normal['id']}/mark-verdict")

    assert response.status_code == 400
