import json
import asyncio
from dataclasses import dataclass, field

import pytest
from sqlalchemy import select

from app.api.chats import get_llm_gateway
from app.db.base import Agent, Message
from app.db.session import get_db
from app.main import app
from app.services.llm_gateway import LLMResponse
from app.services.openrouter_models import normalize_openrouter_endpoint, normalize_openrouter_model
from app.services.structured_response import validate_legal_response


@dataclass
class FakeGateway:
    calls: list[tuple[str, str]]
    response_formats: list[dict | None] = field(default_factory=list)

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        self.response_formats.append(response_format)
        if response_format is None:
            return LLMResponse(
                content=f"Обычный ответ {agent.display_name}",
                model_id=agent.model_name,
                provider_code=agent.provider_code,
                input_tokens=100,
                output_tokens=50,
            )
        agreement = None
        if agent.code in {"lawyer_2", "lawyer_3"}:
            agreement = {"agreed_points": ["История учтена"], "disagreed_points": [], "unresolved_points": []}
        return LLMResponse(
            content=json.dumps(
                {
                    "answer_mode": "final_verdict",
                    "visible_answer": None,
                    "summary": f"Ответ {agent.display_name}",
                    "risk": "yellow",
                    "findings": [{"title": "Вывод", "description": "Нужна проверка источника"}],
                    "sources": [
                        {
                            "source_type": "law_unconfirmed",
                            "document_id": None,
                            "title": "Закон не подтвержден",
                            "document_number": None,
                            "revision_date": None,
                            "article_or_point": None,
                            "quote": "нужно проверить",
                            "verification_status": "pending",
                        }
                    ],
                    "meaning_for_factory": "Для завода нужен контроль ответственного специалиста.",
                    "actions": ["Проверить источник"],
                    "confidence": "medium",
                    "approval_required": "none",
                    "agreement": agreement,
                },
                ensure_ascii=False,
            ),
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=100,
            output_tokens=50,
        )


def _insert_agent_message(chat_id: int, agent_code: str, content: str) -> None:
    async def insert() -> None:
        db_context = app.dependency_overrides[get_db]()
        db = await anext(db_context)
        try:
            agent = (await db.execute(select(Agent).where(Agent.code == agent_code))).scalar_one()
            db.add(
                Message(
                    chat_id=chat_id,
                    role="assistant",
                    author_type={"lawyer_1": "agent1", "lawyer_2": "agent2", "lawyer_3": "agent3"}[agent_code],
                    content=content,
                    agent_id=agent.id,
                )
            )
            await db.commit()
        finally:
            await db_context.aclose()

    asyncio.run(insert())


def test_invoke_calls_only_selected_lawyer_and_saves_metadata(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Общий чат"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Первый вопрос"})
    assert client.get("/api/agents").status_code == 200
    _insert_agent_message(chat_id, "lawyer_1", "Ответ юриста 1")
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Последний вопрос"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 200
    payload = response.json()
    assert [call[0] for call in fake_gateway.calls] == ["lawyer_2"]
    assert "Пользователь: Первый вопрос" in fake_gateway.calls[0][1]
    assert "Юрист 1: Ответ юриста 1" in fake_gateway.calls[0][1]
    assert "Пользователь: Последний вопрос" in fake_gateway.calls[0][1]
    assert payload["author_type"] == "agent2"
    assert payload["content"].startswith("Обычный ответ")
    assert payload["structured_payload"] is None
    assert payload["source_check_status"] == "not_checked"
    assert payload["is_verdict"] is False
    assert fake_gateway.response_formats == [None]
    assert payload["model_id"]
    assert payload["provider_code"] == "cloudflare"
    assert payload["input_tokens"] == 100
    assert payload["output_tokens"] == 50
    assert payload["cost_usd"] == "0.000007"

    costs = client.get(f"/api/chats/{chat_id}/costs").json()
    assert costs[0]["model_id"] == payload["model_id"]
    assert costs[0]["provider_code"] == "cloudflare"


@pytest.mark.parametrize(
    ("agent_code", "author_type"),
    [("lawyer_1", "agent1"), ("lawyer_2", "agent2"), ("lawyer_3", "agent3")],
)
def test_pre_verdict_invoke_is_plain_text_for_every_lawyer(client, agent_code: str, author_type: str) -> None:
    gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Pre-verdict"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Дайте предварительное мнение"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": agent_code})

    assert response.status_code == 200
    body = response.json()
    assert body["author_type"] == author_type
    assert body["content"].startswith("Обычный ответ")
    assert body["structured_payload"] is None
    assert body["is_verdict"] is False
    assert gateway.response_formats == [None]


def test_invoke_context_includes_chat_metadata(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Договор поставки", "section": "Контракты"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь договор"})
    client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    context = fake_gateway.calls[0][1]
    assert "Раздел: Контракты" in context
    assert "Название: Договор поставки" in context


def test_invoke_context_includes_current_question_and_continuation_footer(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Тест"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Текущий вопрос"})
    client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    context = fake_gateway.calls[0][1]
    assert "Текущий вопрос пользователя:" in context
    assert "Используй историю чата" in context


def test_invoke_rejects_disallowed_provider(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway
    client.patch("/api/admin/providers/cloudflare", json={"is_allowlisted": False})
    chat_id = client.post("/api/chats", json={"title": "Provider test"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Question"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 400
    assert fake_gateway.calls == []


def test_lawyer_1_and_2_must_use_distinct_providers(client) -> None:
    response = client.patch("/api/admin/agents/lawyer_2", json={"provider_code": "novita"})

    assert response.status_code == 400
    assert "разных провайдеров" in response.json()["detail"]


def test_openrouter_model_normalization() -> None:
    model = normalize_openrouter_model(
        {
            "id": "qwen/qwen3.7-plus",
            "name": "Qwen Plus",
            "context_length": 1000000,
            "architecture": {"input_modalities": ["text", "image"]},
            "pricing": {"prompt": "0.00000032", "completion": "0.00000128"},
            "supported_parameters": ["structured_outputs"],
        }
    )

    assert model.model_id == "qwen/qwen3.7-plus"
    assert model.provider == "qwen"
    assert model.context_length == 1000000
    assert model.supports_vision is True
    assert model.is_free is False


def test_openrouter_endpoint_normalization_uses_endpoint_provider_tag() -> None:
    model = normalize_openrouter_endpoint(
        {
            "id": "google/gemma-4-26b-a4b-it:free",
            "name": "Google Gemma",
            "context_length": 262144,
            "architecture": {"input_modalities": ["text"]},
        },
        {
            "model_id": "google/gemma-4-26b-a4b-it",
            "model_name": "Google Gemma",
            "provider_name": "DekaLLM",
            "tag": "dekallm/bf16",
            "status": 0,
            "pricing": {"prompt": "0.00000006", "completion": "0.00000033"},
            "context_length": 262144,
        },
    )

    assert model.model_id == "google/gemma-4-26b-a4b-it"
    assert model.provider == "dekallm/bf16"
    assert model.is_available is True


# --- Fallback behavior when LLM returns invalid JSON ---

@dataclass
class FakeGatewayRawText:
    """Returns plain text (not JSON) on every call."""
    calls: list[str]

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append(agent.code)
        return LLMResponse(
            content="Закон нарушен. Необходима проверка договора и оплата задолженности.",
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=50,
            output_tokens=30,
        )


def test_invoke_saves_fallback_when_json_invalid(client) -> None:
    fake_gateway = FakeGatewayRawText(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Тест"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Что делать с долгом?"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    msg = response.json()
    assert msg["author_type"] == "agent1"
    assert "Закон нарушен" in msg["content"]
    assert msg["model_id"] is not None
    assert msg["input_tokens"] > 0


def test_invoke_fallback_is_not_system_message(client) -> None:
    fake_gateway = FakeGatewayRawText(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Тест"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Вопрос"})
    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 200
    assert response.json()["author_type"] == "agent2"


def test_invoke_fallback_message_appears_in_chat_messages(client) -> None:
    fake_gateway = FakeGatewayRawText(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Тест контекст"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Вопрос"})
    client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    messages = client.get(f"/api/chats/{chat_id}/messages").json()
    agent_messages = [m for m in messages if m["author_type"] == "agent1"]
    assert len(agent_messages) == 1
    assert agent_messages[0]["content"]


@dataclass
class FakeGatewayUnexpectedJson:
    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        return LLMResponse(
            content='{"secret_backend_field": true}',
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=1,
            output_tokens=1,
        )


def test_normal_mode_does_not_show_raw_json(client) -> None:
    app.dependency_overrides[get_llm_gateway] = lambda: FakeGatewayUnexpectedJson()
    chat_id = client.post("/api/chats", json={"title": "Safe text"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Ответьте текстом"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    assert response.json()["content"] == "Ответ получен в неподдерживаемом формате. Попросите юриста ответить обычным текстом."
    assert "secret_backend_field" not in response.json()["content"]


# --- Parser robustness ---

def test_validate_legal_response_parses_fenced_json_block() -> None:
    valid_payload = {
        "answer_mode": "final_verdict",
        "visible_answer": None,
        "summary": "Тест фенсд",
        "risk": "green",
        "findings": [],
        "sources": [],
        "meaning_for_factory": "Нет рисков",
        "actions": [],
        "confidence": "high",
        "approval_required": "none",
        "agreement": None,
    }
    fenced = f"```json\n{json.dumps(valid_payload, ensure_ascii=False)}\n```"
    result = validate_legal_response(fenced, "lawyer_1")
    assert result.summary == "Тест фенсд"
    assert result.answer_mode == "final_verdict"


def test_validate_legal_response_parses_json_with_surrounding_text() -> None:
    valid_payload = {
        "answer_mode": "final_verdict",
        "visible_answer": None,
        "summary": "Тест окружение",
        "risk": "yellow",
        "findings": [],
        "sources": [],
        "meaning_for_factory": "Проверить",
        "actions": [],
        "confidence": "medium",
        "approval_required": "none",
        "agreement": None,
    }
    content = f"Вот мой анализ:\n{json.dumps(valid_payload, ensure_ascii=False)}\nНадеюсь это помогло."
    result = validate_legal_response(content, "lawyer_1")
    assert result.summary == "Тест окружение"
