import asyncio
from dataclasses import dataclass, field

from sqlalchemy import select

from app.api.chats import get_llm_gateway
from app.db.base import Agent, Message
from app.db.session import get_db
from app.main import app
from app.schemas.messages import MessageRead
from app.services.current_user import CurrentUser, get_current_user
from app.services.llm_gateway import LLMResponse


@dataclass
class DocumentGateway:
    calls: list[tuple[str, str]] = field(default_factory=list)
    content: str = "Черновик письма по активному вердикту."

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        return LLMResponse(
            content=self.content,
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=10,
            output_tokens=20,
        )


def _create_chat(client, title: str = "Stage 5") -> int:
    return client.post("/api/chats", json={"title": title}).json()["id"]


def _create_message(client, chat_id: int, author_type: str, content: str = "Text", **extra) -> dict:
    if author_type == "user":
        response = client.post(f"/api/chats/{chat_id}/messages", json={"content": content})
        assert response.status_code == 201
        return response.json()

    assert client.get("/api/agents").status_code == 200

    async def insert() -> dict:
        db_context = app.dependency_overrides[get_db]()
        db = await anext(db_context)
        try:
            agent_code = {"agent1": "lawyer_1", "agent2": "lawyer_2", "agent3": "lawyer_3"}[author_type]
            agent = (await db.execute(select(Agent).where(Agent.code == agent_code))).scalar_one()
            if agent_code in {"lawyer_2", "lawyer_3"}:
                structured_payload = extra.pop("structured_payload", None)
                if not isinstance(structured_payload, dict) or structured_payload.get("type") != "verdict":
                    structured_payload = {
                        "type": "verdict",
                        "lawyer_id": agent_code,
                        "jurisdiction": "UZ",
                        "short_conclusion": content,
                        "facts_established": [],
                        "facts_missing": [],
                        "legal_sources": [],
                        "analysis": [],
                        "risks": [],
                        "recommended_actions": [],
                        "confidence": "medium",
                    }
                extra.setdefault("structured_payload", structured_payload)
                extra.setdefault("source_check_status", "confirmed")
                extra.setdefault("document_generation_allowed", True)
            message = Message(
                chat_id=chat_id,
                role="assistant",
                author_type=author_type,
                content=content,
                agent_id=agent.id,
                **extra,
            )
            db.add(message)
            await db.commit()
            await db.refresh(message)
            return MessageRead.model_validate(message).model_dump(mode="json")
        finally:
            await db_context.aclose()

    return asyncio.run(insert())


def _mark_verdict(client, chat_id: int, message_id: int) -> dict:
    response = client.post(f"/api/chats/{chat_id}/messages/{message_id}/mark-verdict")
    assert response.status_code == 200
    return response.json()


def _generate_document(client, chat_id: int, gateway: DocumentGateway | None = None) -> dict:
    if gateway is not None:
        app.dependency_overrides[get_llm_gateway] = lambda: gateway
    response = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={"agent_code": "lawyer_1", "document_type": "claim_letter", "title": "Письмо клиенту"},
    )
    assert response.status_code == 201
    return response.json()


def test_only_lawyer_message_can_be_verdict_and_only_one_is_active(client) -> None:
    chat_id = _create_chat(client)
    user_message = _create_message(client, chat_id, "user", "Вопрос")
    lawyer_1_message = _create_message(client, chat_id, "agent1", "Предварительный вывод")
    first = _create_message(client, chat_id, "agent2", "Первый вердикт")
    second = _create_message(client, chat_id, "agent3", "Второй вердикт")

    rejected = client.post(f"/api/chats/{chat_id}/messages/{user_message['id']}/mark-verdict")
    assert rejected.status_code == 400
    lawyer_1_rejected = client.post(f"/api/chats/{chat_id}/messages/{lawyer_1_message['id']}/mark-verdict")
    assert lawyer_1_rejected.status_code == 400

    assert _mark_verdict(client, chat_id, first["id"])["is_verdict"] is True
    assert client.get(f"/api/chats/{chat_id}/verdict").json()["id"] == first["id"]

    assert _mark_verdict(client, chat_id, second["id"])["is_verdict"] is True
    messages = client.get(f"/api/chats/{chat_id}/messages").json()
    verdict_flags = {message["id"]: message["is_verdict"] for message in messages}
    assert verdict_flags[first["id"]] is False
    assert verdict_flags[second["id"]] is True
    assert client.get(f"/api/chats/{chat_id}").json()["active_verdict_message_id"] == second["id"]

    cleared = client.delete(f"/api/chats/{chat_id}/verdict")
    assert cleared.status_code == 200
    assert cleared.json()["active_verdict_message_id"] is None
    assert client.get(f"/api/chats/{chat_id}/verdict").status_code == 404


def test_generate_document_requires_active_verdict_and_uses_only_that_context(client) -> None:
    chat_id = _create_chat(client)
    _create_message(client, chat_id, "agent1", "Раннее мнение нельзя брать")
    gateway = DocumentGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway

    no_verdict = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={"agent_code": "lawyer_1", "document_type": "claim_letter", "title": "Письмо"},
    )
    assert no_verdict.status_code == 400
    assert "Сначала нужно пометить сообщение юриста как вердикт" in no_verdict.json()["detail"]
    assert gateway.calls == []

    verdict = _create_message(
        client,
        chat_id,
        "agent2",
        "Итоговый вердикт",
        risk="yellow",
        approval_required="none",
        structured_payload={"type": "verdict", "short_conclusion": "Итоговый вердикт"},
    )
    _mark_verdict(client, chat_id, verdict["id"])
    document = _generate_document(client, chat_id, gateway)

    assert document["title"] == "Письмо клиенту"
    assert document["document_type"] == "claim_letter"
    assert document["status"] == "draft"
    assert document["verdict_message_id"] == verdict["id"]
    assert document["content"] == gateway.content
    assert gateway.calls[0][0] == "lawyer_1"
    assert "<ACTIVE_VERDICT>" in gateway.calls[0][1]
    assert "Итоговый вердикт" in gateway.calls[0][1]
    assert "Запрещено использовать ранние мнения" in gateway.calls[0][1]


def test_red_or_needs_review_verdict_creates_needs_review_document_and_draft_stays_draft(client) -> None:
    red_chat = _create_chat(client)
    red_verdict = _create_message(client, red_chat, "agent3", "Красный риск", risk="red", approval_required="director")
    _mark_verdict(client, red_chat, red_verdict["id"])
    assert _generate_document(client, red_chat, DocumentGateway())["status"] == "needs_review"

    draft_chat = _create_chat(client)
    draft_verdict = _create_message(client, draft_chat, "agent2", "Зелёный риск", risk="green", approval_required="none")
    _mark_verdict(client, draft_chat, draft_verdict["id"])
    assert _generate_document(client, draft_chat, DocumentGateway())["status"] == "draft"


def test_generated_document_edit_export_send_to_chat_and_audit(client) -> None:
    chat_id = _create_chat(client)
    verdict = _create_message(client, chat_id, "agent2", "Вердикт", risk="green", approval_required="none")
    _mark_verdict(client, chat_id, verdict["id"])
    gateway = DocumentGateway()
    document = _generate_document(client, chat_id, gateway)

    updated = client.patch(
        f"/api/generated-documents/{document['id']}",
        json={"content": "Изменённый черновик", "title": "Обновлённое письмо"},
    )
    assert updated.status_code == 200
    assert updated.json()["content"] == "Изменённый черновик"
    assert client.get(f"/api/generated-documents/{document['id']}").json()["content"] == "Изменённый черновик"

    docx = client.get(f"/api/generated-documents/{document['id']}/download.docx")
    assert docx.status_code == 200
    assert docx.headers["content-type"].startswith(
        "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    )
    assert docx.content.startswith(b"PK")

    pdf = client.get(f"/api/generated-documents/{document['id']}/download.pdf")
    assert pdf.status_code == 200
    assert pdf.headers["content-type"].startswith("application/pdf")
    assert pdf.content.startswith(b"%PDF")

    calls_before_send = len(gateway.calls)
    sent = client.post(f"/api/generated-documents/{document['id']}/send-to-chat")
    assert sent.status_code == 200
    assert len(gateway.calls) == calls_before_send
    messages = client.get(f"/api/chats/{chat_id}/messages").json()
    assert messages[-1]["author_type"] == "user"
    assert "Документ отправлен в общий чат" in messages[-1]["content"]

    # Пользователь после возврата документа может сам выбрать юриста обычным composer flow.
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    invoke = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_2"})
    assert invoke.status_code in {200, 502}
    assert gateway.calls[-1][0] == "lawyer_2"

    actions = [item["action"] for item in client.get("/api/admin/audit-logs").json()]
    assert "verdict.marked" in actions
    assert "generated_document.created_from_verdict" in actions
    assert "generated_document.edited" in actions
    assert "generated_document.exported_docx" in actions
    assert "generated_document.exported_pdf" in actions
    assert "generated_document.sent_to_chat" in actions


def test_generated_document_approval_status_and_role_check(client) -> None:
    chat_id = _create_chat(client)
    verdict = _create_message(client, chat_id, "agent2", "Вердикт", risk="green", approval_required="none")
    _mark_verdict(client, chat_id, verdict["id"])
    document = _generate_document(client, chat_id, DocumentGateway())

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=10, role="sales")
    assert client.post(f"/api/generated-documents/{document['id']}/approve").status_code == 403

    app.dependency_overrides[get_current_user] = lambda: CurrentUser(id=11, role="director")
    requested = client.post(f"/api/generated-documents/{document['id']}/request-approval")
    assert requested.status_code == 200
    assert requested.json()["status"] == "needs_review"
    approved = client.post(f"/api/generated-documents/{document['id']}/approve")
    assert approved.status_code == 200
    assert approved.json()["status"] == "approved"
    rejected = client.post(f"/api/generated-documents/{document['id']}/reject")
    assert rejected.status_code == 200
    assert rejected.json()["status"] == "rejected"

    approvals = client.get(f"/api/generated-documents/{document['id']}/approvals").json()
    assert [event["action"] for event in approvals] == ["request", "approve", "reject"]
    assert approvals[-1]["entity_type"] == "generated_document"
    assert approvals[-1]["new_status"] == "rejected"
