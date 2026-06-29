import json
from dataclasses import dataclass, field

from app.api.chats import get_llm_gateway
from app.core.config import settings
from app.main import app
from app.services.current_user import CurrentUser, get_current_user
from app.services.llm_gateway import LLMResponse


def legal_payload(**overrides) -> dict:
    payload = {
        "summary": "Краткий вывод",
        "risk": "yellow",
        "findings": [{"title": "Проверка", "description": "Описание"}],
        "sources": [
            {
                "source_type": "law_unconfirmed",
                "document_id": None,
                "title": "Неподтвержденный закон",
                "document_number": None,
                "revision_date": None,
                "article_or_point": None,
                "quote": "нужно проверить",
                "verification_status": "pending",
            }
        ],
        "meaning_for_factory": "Нужна проверка ответственным специалистом.",
        "actions": ["Проверить источник"],
        "confidence": "medium",
        "approval_required": "none",
        "agreement": None,
    }
    payload.update(overrides)
    return payload


@dataclass
class SequenceGateway:
    responses: list[str]
    calls: list[tuple[str, str]] = field(default_factory=list)

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        content = self.responses.pop(0)
        return LLMResponse(
            content=content,
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=100,
            output_tokens=50,
        )


def upload_txt(client, text: str, chat_id: int | None = None):
    data = {"sensitivity": "internal"}
    if chat_id is not None:
        data["chat_id"] = str(chat_id)
    return client.post(
        "/api/documents/upload",
        data=data,
        files={"file": ("source.txt", text.encode(), "text/plain")},
    )


def invoke_with_response(client, agent_code: str, response_payload: dict | str | list[dict | str], chat_id: int | None = None):
    if chat_id is None:
        chat_id = client.post("/api/chats", json={"title": "Stage 4"}).json()["id"]
        client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь договор"})
    payloads = response_payload if isinstance(response_payload, list) else [response_payload]
    contents = [payload if isinstance(payload, str) else json.dumps(payload, ensure_ascii=False) for payload in payloads]
    gateway = SequenceGateway(contents)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": agent_code})
    return chat_id, response, gateway


def test_normal_mode_does_not_save_structured_json(client) -> None:
    _, response, _ = invoke_with_response(client, "lawyer_1", legal_payload())

    assert response.status_code == 200
    payload = response.json()
    assert payload["content"] == "Краткий вывод"
    assert payload["structured_payload"] is None
    assert payload["risk"] is None
    assert payload["confidence"] is None


def test_unknown_field_and_invalid_json_use_fallback(client) -> None:
    # JSON with unknown extra field → Pydantic rejects → fallback with raw text, not a 502
    bad_payload = legal_payload(extra_field="forbidden")
    _, response, _ = invoke_with_response(client, "lawyer_1", [bad_payload, bad_payload])
    assert response.status_code == 200
    assert response.json()["author_type"] == "agent1"

    # Plain non-JSON text → fallback with raw content visible
    _, invalid_response, _ = invoke_with_response(client, "lawyer_1", ["not-json", "still-not-json"])
    assert invalid_response.status_code == 200
    assert invalid_response.json()["author_type"] == "agent1"


def test_normal_mode_does_not_attempt_json_repair(client) -> None:
    chat_id = client.post("/api/chats", json={"title": "Repair"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь"})
    gateway = SequenceGateway(["broken", json.dumps(legal_payload(), ensure_ascii=False)])
    app.dependency_overrides[get_llm_gateway] = lambda: gateway

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    assert len(gateway.calls) == 1
    assert response.json()["input_tokens"] == 100


def test_normal_mode_does_not_claim_citation_verification(client) -> None:
    chat_id = client.post("/api/chats", json={"title": "Quotes"}).json()["id"]
    doc = upload_txt(client, "Поставка кабеля выполняется до 20 июня.", chat_id).json()["document"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь срок"})
    payload = legal_payload(
        risk="green",
        confidence="high",
        sources=[
            {
                "source_type": "uploaded_document",
                "document_id": doc["id"],
                "title": "Договор",
                "document_number": None,
                "revision_date": None,
                "article_or_point": None,
                "quote": "Поставка кабеля выполняется до 20 июня.",
                "verification_status": "pending",
            }
        ],
    )
    _, confirmed_response, _ = invoke_with_response(client, "lawyer_1", payload, chat_id)
    assert confirmed_response.status_code == 200
    assert confirmed_response.json()["source_check_status"] == "not_checked"
    assert confirmed_response.json()["structured_payload"] is None

    chat_id = client.post("/api/chats", json={"title": "Missing quote"}).json()["id"]
    doc = upload_txt(client, "Есть только один пункт.", chat_id).json()["document"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь"})
    payload["sources"][0]["document_id"] = doc["id"]
    payload["sources"][0]["quote"] = "Такой цитаты нет"
    _, missing_response, _ = invoke_with_response(client, "lawyer_1", payload, chat_id)
    body = missing_response.json()
    assert body["source_check_status"] == "not_checked"
    assert body["risk"] is None
    assert body["confidence"] is None


def test_normal_mode_ignores_model_risk_confidence_and_approval_fields(client) -> None:
    payload = legal_payload(risk="green", confidence="high")
    _, response, _ = invoke_with_response(client, "lawyer_1", payload)

    body = response.json()
    assert body["source_check_status"] == "not_checked"
    assert body["risk"] is None
    assert body["confidence"] is None
    assert body["approval_required"] is None


def test_normal_lawyer_2_and_3_do_not_require_structured_agreement(client) -> None:
    no_agreement = legal_payload(agreement=None)
    _, missing_agreement, _ = invoke_with_response(client, "lawyer_2", [no_agreement, no_agreement])
    assert missing_agreement.status_code == 200
    assert missing_agreement.json()["author_type"] == "agent2"
    assert missing_agreement.json()["structured_payload"] is None

    arbiter_payload = legal_payload(
        agreement={"agreed_points": [], "disagreed_points": [], "unresolved_points": ["Спорный пункт"]},
    )
    _, response, _ = invoke_with_response(client, "lawyer_3", arbiter_payload)
    assert response.status_code == 200
    body = response.json()
    assert body["structured_payload"] is None
    assert body["is_verdict"] is False


def test_red_flag_moves_chat_to_needs_review_but_normal_topic_does_not(client) -> None:
    red_chat = client.post("/api/chats", json={"title": "Red"}).json()["id"]
    client.post(f"/api/chats/{red_chat}/messages", json={"content": "Нужно увольнение сотрудника"})
    assert client.get(f"/api/chats/{red_chat}").json()["approval_status"] == "needs_review"

    normal_chat = client.post("/api/chats", json={"title": "Normal"}).json()["id"]
    client.post(f"/api/chats/{normal_chat}/messages", json={"content": "Проверить обычный договор"})
    assert client.get(f"/api/chats/{normal_chat}").json()["approval_status"] == "draft"


def test_approval_journal_and_backend_role_check(client) -> None:
    chat_id = client.post("/api/chats", json={"title": "Approval"}).json()["id"]
    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=5, role="sales")
    assert client.post(f"/api/chats/{chat_id}/approve").status_code == 403

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=1, role="director")
    assert client.post(f"/api/chats/{chat_id}/request-approval").json()["approval_status"] == "needs_review"
    assert client.post(f"/api/chats/{chat_id}/approve").json()["approval_status"] == "approved"
    approvals = client.get(f"/api/chats/{chat_id}/approvals").json()
    assert [event["action"] for event in approvals] == ["request", "approve"]
    assert approvals[-1]["new_status"] == "approved"


def test_fallback_extracts_visible_answer_from_json_like_text(client) -> None:
    # JSON that fails Pydantic (extra field) but has visible_answer → shown, not raw JSON
    payload_with_visible = legal_payload(
        answer_mode="preliminary_opinion",
        visible_answer="Договор нарушает статью 432 ГК РФ.",
        extra_field="forbidden",
    )
    _, response, _ = invoke_with_response(client, "lawyer_1", [payload_with_visible, payload_with_visible])
    assert response.status_code == 200
    body = response.json()
    assert body["content"] == "Договор нарушает статью 432 ГК РФ."
    assert not body["content"].startswith("{")


def test_fallback_extracts_summary_when_no_visible_answer(client) -> None:
    # JSON fails validation, no visible_answer → summary used, not raw JSON
    payload_no_visible = legal_payload(
        answer_mode="preliminary_opinion",
        extra_field="forbidden",
    )
    _, response, _ = invoke_with_response(client, "lawyer_1", [payload_no_visible, payload_no_visible])
    assert response.status_code == 200
    body = response.json()
    assert not body["content"].startswith("{")
    assert "Краткий вывод" in body["content"]


def test_fallback_plain_prose_shown_as_is(client) -> None:
    # Plain text (not JSON) → returned as content unchanged
    _, response, _ = invoke_with_response(client, "lawyer_1", ["Закон не нарушен.", "Закон не нарушен."])
    assert response.status_code == 200
    assert response.json()["content"] == "Закон не нарушен."


def test_monthly_budget_blocks_non_admin_when_enabled(client, monkeypatch) -> None:
    monkeypatch.setattr(settings, "monthly_budget_usd", 0.000001)
    monkeypatch.setattr(settings, "block_expensive_calls", True)

    chat_id, first_response, _ = invoke_with_response(client, "lawyer_1", legal_payload())
    assert first_response.status_code == 200

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=1, role="sales")
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Еще вопрос"})
    gateway = SequenceGateway([json.dumps(legal_payload(), ensure_ascii=False)])
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    blocked = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert blocked.status_code == 402
    assert gateway.calls == []
