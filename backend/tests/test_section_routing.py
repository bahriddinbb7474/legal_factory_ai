from dataclasses import dataclass, field
from unittest.mock import AsyncMock

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.legal_retriever import legal_retriever
from app.services.llm_gateway import LLMResponse


@dataclass
class RecordingGateway:
    calls: list[tuple[str, str]] = field(default_factory=list)

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        return LLMResponse(
            content="Обычный текстовый ответ",
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=10,
            output_tokens=10,
        )


def _chat_with_message(client, section: str, content: str) -> int:
    chat = client.post("/api/chats", json={"title": "Section routing", "section": section})
    assert chat.status_code == 201
    chat_id = chat.json()["id"]
    message = client.post(f"/api/chats/{chat_id}/messages", json={"content": content})
    assert message.status_code == 201
    return chat_id


def test_template_section_uses_plain_drafting_policy_without_default_rag(client, monkeypatch) -> None:
    gateway = RecordingGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    retrieve = AsyncMock(return_value=[])
    monkeypatch.setattr(legal_retriever, "retrieve", retrieve)
    chat_id = _chat_with_message(client, "template_letters", "Подготовь обычное письмо поставщику")

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    assert response.json()["structured_payload"] is None
    assert response.json()["is_verdict"] is False
    retrieve.assert_not_awaited()
    context = gateway.calls[0][1]
    assert "Section code: template_letters" in context
    assert "Section group: template_documents" in context
    assert "Section label: Письма" in context
    assert "no RAG, legal conclusion, or verdict by default" in context


def test_legal_section_lawyer_1_context_requires_source_check(client, monkeypatch) -> None:
    gateway = RecordingGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    retrieve = AsyncMock(return_value=[])
    monkeypatch.setattr(legal_retriever, "retrieve", retrieve)
    chat_id = _chat_with_message(client, "legal_hr", "Можно ли применить взыскание?")

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    retrieve.assert_awaited_once()
    context = gateway.calls[0][1]
    assert "Section code: legal_hr" in context
    assert "Section group: legal_questions" in context
    assert "Section label: HR / Трудовое право" in context
    assert "Lawyer 1 must request/check active official sources" in context


def test_template_section_rejects_verdict_shortcut(client) -> None:
    chat_id = _chat_with_message(client, "template_letters", "Оформи свой вердикт")

    response = client.post(
        f"/api/chats/{chat_id}/invoke",
        json={"agent_code": "lawyer_2", "mode": "verdict"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Verdict mode is unavailable in template sections. Select a legal section."


def test_template_order_discipline_keeps_red_topic_override(client) -> None:
    chat_id = _chat_with_message(client, "template_orders", "Подготовь дисциплинарное взыскание сотруднику")

    chat = client.get(f"/api/chats/{chat_id}").json()
    message = client.get(f"/api/chats/{chat_id}/messages").json()[0]
    assert chat["approval_status"] == "needs_review"
    assert "employee_dismissal" in message["red_flag_codes"]


def test_template_letter_tax_fine_keeps_red_topic_override(client) -> None:
    chat_id = _chat_with_message(client, "template_letters", "Ответ налоговому органу о штрафе")

    chat = client.get(f"/api/chats/{chat_id}").json()
    message = client.get(f"/api/chats/{chat_id}/messages").json()[0]
    assert chat["approval_status"] == "needs_review"
    assert "tax_authority_response" in message["red_flag_codes"]
    assert "fine_or_penalty" in message["red_flag_codes"]


def test_legal_hr_discipline_keeps_red_topic_override(client) -> None:
    chat_id = _chat_with_message(client, "legal_hr", "Нужно дисциплинарное взыскание")

    chat = client.get(f"/api/chats/{chat_id}").json()
    message = client.get(f"/api/chats/{chat_id}/messages").json()[0]
    assert chat["approval_status"] == "needs_review"
    assert "employee_dismissal" in message["red_flag_codes"]
