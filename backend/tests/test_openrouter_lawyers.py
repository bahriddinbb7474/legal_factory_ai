from dataclasses import dataclass

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMResponse
from app.services.openrouter_models import normalize_openrouter_model


@dataclass
class FakeGateway:
    calls: list[tuple[str, str]]

    async def invoke(self, agent, chat_context: str) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        return LLMResponse(
            content=f"Ответ {agent.display_name}",
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=100,
            output_tokens=50,
        )


def test_invoke_calls_only_selected_lawyer_and_saves_metadata(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway

    chat_id = client.post("/api/chats", json={"title": "Общий чат"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "Первый вопрос"})
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "agent1", "content": "Ответ юриста 1"})
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "Последний вопрос"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 200
    payload = response.json()
    assert [call[0] for call in fake_gateway.calls] == ["lawyer_2"]
    assert "Пользователь: Первый вопрос" in fake_gateway.calls[0][1]
    assert "Юрист 1: Ответ юриста 1" in fake_gateway.calls[0][1]
    assert "Пользователь: Последний вопрос" in fake_gateway.calls[0][1]
    assert payload["author_type"] == "agent2"
    assert payload["model_id"]
    assert payload["provider_code"] == "deepseek"
    assert payload["input_tokens"] == 100
    assert payload["output_tokens"] == 50
    assert payload["cost_usd"] == "0.000120"

    costs = client.get(f"/api/chats/{chat_id}/costs").json()
    assert costs[0]["model_id"] == payload["model_id"]
    assert costs[0]["provider_code"] == "deepseek"


def test_invoke_rejects_disallowed_provider(client) -> None:
    fake_gateway = FakeGateway(calls=[])
    app.dependency_overrides[get_llm_gateway] = lambda: fake_gateway
    client.patch("/api/admin/providers/deepseek", json={"is_allowlisted": False})
    chat_id = client.post("/api/chats", json={"title": "Provider test"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "Question"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})

    assert response.status_code == 400
    assert fake_gateway.calls == []


def test_lawyer_1_and_2_must_use_distinct_providers(client) -> None:
    response = client.patch("/api/admin/agents/lawyer_2", json={"provider_code": "qwen"})

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
