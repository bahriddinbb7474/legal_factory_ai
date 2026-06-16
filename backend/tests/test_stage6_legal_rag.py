import json
from dataclasses import dataclass, field

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMResponse


@dataclass
class RagGateway:
    response_payload: dict
    calls: list[tuple[str, str]] = field(default_factory=list)

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        return LLMResponse(
            content=json.dumps(self.response_payload, ensure_ascii=False),
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=10,
            output_tokens=10,
        )


def legal_payload(source: dict, **overrides) -> dict:
    payload = {
        "summary": "Краткий вывод",
        "risk": "green",
        "findings": [{"title": "Вывод", "description": "Описание"}],
        "sources": [source],
        "meaning_for_factory": "Для завода нужно соблюдать пункт.",
        "actions": ["Проверить документы"],
        "confidence": "high",
        "approval_required": "none",
        "agreement": None,
    }
    payload.update(overrides)
    return payload


def create_source(client, document_type: str, raw_text: str, **overrides) -> dict:
    data = {
        "document_type": document_type,
        "title": overrides.pop("title", "Тестовый акт"),
        "document_number": overrides.pop("document_number", "№999"),
        "source_name": overrides.pop("source_name", "LEX.UZ"),
        "source_url": overrides.pop("source_url", "https://lex.uz/test"),
        "adoption_date": overrides.pop("adoption_date", "2026-01-01"),
        "revision_date": overrides.pop("revision_date", "2026-06-01"),
        "language": overrides.pop("language", "ru"),
        "status": overrides.pop("status", "active"),
        "official_status": overrides.pop("official_status", "official"),
        "raw_text": raw_text,
    }
    data.update(overrides)
    response = client.post("/api/admin/legal-sources", data=data)
    assert response.status_code == 201
    return response.json()


def test_upload_legal_source_raw_text_file_metadata_pp_pkm_and_reindex(client) -> None:
    raw = "Статья 1. Поставка кабеля регулируется договором.\n\nСтатья 2. Срок поставки фиксируется письменно."
    source = create_source(client, "law", raw, title="Закон о тесте")
    assert source["chunks_count"] == 2
    assert source["chunks"][0]["article_or_point"] == "Статья 1"

    file_response = client.post(
        "/api/admin/legal-sources",
        data={
            "document_type": "presidential_resolution",
            "title": "ПП тест",
            "document_number": "ПП №1",
            "source_name": "LEX.UZ",
            "source_url": "https://lex.uz/pp",
            "adoption_date": "2026-01-01",
            "revision_date": "2026-02-01",
            "language": "ru",
            "status": "active",
            "official_status": "official",
        },
        files={"file": ("pp.txt", "Пункт 1. Президентское постановление действует.".encode("utf-8"), "text/plain")},
    )
    assert file_response.status_code == 201
    assert file_response.json()["document_type"] == "presidential_resolution"

    pkm = create_source(
        client,
        "cabinet_resolution",
        "ПКМ №999 от 01.01.2026\n\nПункт 1. Кабельный завод обязан хранить техническую документацию.\n\nПункт 2. Ответственный сотрудник назначается приказом директора.",
        title="ПКМ тест",
        document_number="ПКМ №999",
    )
    assert pkm["document_type"] == "cabinet_resolution"
    assert [chunk["article_or_point"] for chunk in pkm["chunks"]] == ["Пункт 1", "Пункт 2"]

    missing = client.post("/api/admin/legal-sources", data={"document_type": "law", "title": "x"})
    assert missing.status_code == 422

    reindexed = client.post(f"/api/admin/legal-sources/{pkm['id']}/reindex")
    assert reindexed.status_code == 200
    assert reindexed.json()["chunks_count"] == 2


def test_fallback_chunking_freshness_and_inactive_sources(client) -> None:
    no_revision = create_source(client, "standard", "Обычный текст без статей и пунктов.", revision_date=None)
    assert no_revision["needs_revision_check"] is True
    assert "дата редакции" in no_revision["revision_warning"]
    assert no_revision["chunks"][0]["article_or_point"] == "unknown"

    archived = create_source(
        client,
        "cabinet_resolution",
        "Пункт 1. Архивный акт не должен попадать в поиск.",
        title="Архивный ПКМ",
        status="archived",
    )
    outdated = create_source(
        client,
        "presidential_resolution",
        "Пункт 1. Устаревший акт не должен попадать в поиск.",
        title="Устаревший ПП",
        status="outdated",
    )
    active = create_source(
        client,
        "cabinet_resolution",
        "Пункт 1. Кабельный завод обязан хранить техническую документацию.",
        title="Активный ПКМ",
        document_number="ПКМ №999",
    )

    payload = legal_payload(
        {
            "source_type": "law",
            "legal_source_id": active["id"],
            "title": "Активный ПКМ",
            "document_type": "cabinet_resolution",
            "document_number": "ПКМ №999",
            "revision_date": "2026-06-01",
            "article_or_point": "Пункт 1",
            "source_name": "LEX.UZ",
            "source_url": "https://lex.uz/test",
            "quote": "Кабельный завод обязан хранить техническую документацию.",
            "verification_status": "pending",
        }
    )
    gateway = RagGateway(payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "RAG"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "Что должен хранить кабельный завод?"})
    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    context = gateway.calls[0][1]
    assert "<TRUSTED_LEGAL_SOURCE" in context
    assert "<UNTRUSTED_DOCUMENT" not in context
    assert "Активный ПКМ" in context
    assert "Архивный ПКМ" not in context
    assert "Устаревший ПП" not in context
    body = response.json()
    assert body["source_check_status"] == "confirmed"
    assert body["structured_payload"]["sources"][0]["verification_status"] == "confirmed"


def test_law_citation_rules_and_uploaded_document_still_work(client) -> None:
    source = create_source(
        client,
        "cabinet_resolution",
        "Пункт 1. Кабельный завод обязан хранить техническую документацию.",
        title="ПКМ цитаты",
        document_number="ПКМ №999",
    )
    wrong_payload = legal_payload(
        {
            "source_type": "law",
            "legal_source_id": source["id"],
            "title": "ПКМ цитаты",
            "document_type": "cabinet_resolution",
            "document_number": "ПКМ №999",
            "revision_date": "2026-06-01",
            "article_or_point": "Пункт 1",
            "source_name": "LEX.UZ",
            "source_url": "https://lex.uz/test",
            "quote": "Такой цитаты нет.",
            "verification_status": "pending",
        }
    )
    gateway = RagGateway(wrong_payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Wrong quote"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "техническую документацию"})
    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})
    body = response.json()
    assert response.status_code == 200
    assert body["source_check_status"] == "unconfirmed"
    assert body["risk"] == "yellow"
    assert body["confidence"] == "medium"

    law_unconfirmed = legal_payload(
        {
            "source_type": "law_unconfirmed",
            "title": "Непроверенный закон",
            "quote": "нужно проверить",
            "verification_status": "pending",
        }
    )
    gateway = RagGateway(law_unconfirmed)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Unconfirmed"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "любой вопрос"})
    assert client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"}).json()["source_check_status"] == "unconfirmed"

    upload = client.post(
        "/api/documents/upload",
        data={"chat_id": str(chat_id), "sensitivity": "internal"},
        files={"file": ("contract.txt", "Поставка кабеля выполняется в июне.".encode("utf-8"), "text/plain")},
    )
    assert upload.status_code == 201
    doc_id = upload.json()["document"]["id"]
    uploaded_payload = legal_payload(
        {
            "source_type": "uploaded_document",
            "document_id": doc_id,
            "title": "contract.txt",
            "quote": "Поставка кабеля выполняется в июне.",
            "verification_status": "pending",
        }
    )
    gateway = RagGateway(uploaded_payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    client.post(f"/api/chats/{chat_id}/messages", json={"author_type": "user", "content": "поставка кабеля"})
    uploaded_response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})
    assert uploaded_response.json()["source_check_status"] in {"confirmed", "partially_confirmed"}
