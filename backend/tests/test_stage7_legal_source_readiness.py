import json
from dataclasses import dataclass, field

import pytest

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.llm_gateway import LLMResponse
from app.storage.local import local_storage


@dataclass
class Stage7Gateway:
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


@pytest.fixture(autouse=True)
def isolate_storage(tmp_path, monkeypatch) -> None:
    monkeypatch.setattr(local_storage, "base_dir", tmp_path)
    tmp_path.mkdir(parents=True, exist_ok=True)


def create_source(client, raw_text: str, **overrides) -> dict:
    data = {
        "document_type": overrides.pop("document_type", "cabinet_resolution"),
        "title": overrides.pop("title", "ПКМ readiness"),
        "document_number": overrides.pop("document_number", "ПКМ №999"),
        "source_name": overrides.pop("source_name", "LEX.UZ"),
        "source_url": overrides.pop("source_url", "https://lex.uz/docs/999"),
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


def test_legal_source_api_returns_stage7_metadata(client) -> None:
    source = create_source(client, "Пункт 1. Документы проверяются один раз в месяц.")

    listed = client.get("/api/admin/legal-sources").json()[0]

    for field in [
        "document_type",
        "title",
        "document_number",
        "adoption_date",
        "revision_date",
        "source_name",
        "source_url",
        "official_status",
        "status",
        "language",
        "last_checked_at",
        "next_check_due_at",
        "readiness_warnings",
        "readiness_warning_messages",
    ]:
        assert field in listed
    assert listed["id"] == source["id"]
    assert listed["readiness_warnings"] == []


def test_missing_metadata_produces_readiness_warnings(client) -> None:
    source = create_source(
        client,
        "Пункт 1. Неполный источник.",
        document_number="",
        source_url="",
        adoption_date="",
        revision_date="",
    )

    assert {
        "missing_source_url",
        "missing_document_number",
        "missing_adoption_date",
        "missing_revision_date",
        "active_without_revision_date",
        "official_source_without_url",
    }.issubset(set(source["readiness_warnings"]))
    assert source["needs_revision_check"] is True


def test_active_official_without_revision_or_url_and_bad_lexuz_url_warns(client) -> None:
    source = create_source(
        client,
        "Пункт 1. URL должен быть проверен.",
        source_url="https://example.com/not-lex",
        revision_date="",
    )

    assert "active_without_revision_date" in source["readiness_warnings"]
    assert "lexuz_source_with_bad_url" in source["readiness_warnings"]

    official_non_lex = create_source(
        client,
        "Пункт 1. Официальный источник не LEX.",
        title="Не LEX",
        source_name="Some official source",
        source_url="https://official.example/source",
    )
    assert "lexuz_expected_for_official_law" in official_non_lex["readiness_warnings"]


def test_chunks_inspection_endpoint_returns_uploaded_and_reindexed_chunks(client) -> None:
    source = create_source(
        client,
        "Пункт 1. Первый пункт.\n\nПункт 2. Второй пункт.",
    )

    chunks = client.get(f"/api/admin/legal-sources/{source['id']}/chunks")
    assert chunks.status_code == 200
    payload = chunks.json()
    assert len(payload) == 2
    assert payload[0]["article_or_point"] == "Пункт 1"
    assert payload[0]["text_preview"]
    assert payload[0]["char_count"] == len(payload[0]["chunk_text"])

    reindexed = client.post(f"/api/admin/legal-sources/{source['id']}/reindex")
    assert reindexed.status_code == 200
    assert client.get(f"/api/admin/legal-sources/{source['id']}/chunks").json()[1]["article_or_point"] == "Пункт 2"


def test_stage6_law_citation_and_inactive_exclusion_still_work(client) -> None:
    create_source(client, "Пункт 1. Архивный акт не должен попадать в поиск.", title="Архив", status="archived")
    active = create_source(
        client,
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
            "source_url": "https://lex.uz/docs/999",
            "quote": "Кабельный завод обязан хранить техническую документацию.",
            "verification_status": "pending",
        }
    )
    gateway = Stage7Gateway(payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Stage 7.1"}).json()["id"]
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Что обязан хранить кабельный завод?"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    context = gateway.calls[0][1]
    assert "<TRUSTED_LEGAL_SOURCE" in context
    assert "Активный ПКМ" in context
    assert "Архивный акт" not in context
    assert response.json()["source_check_status"] == "not_checked"


def test_draft_future_outdated_and_archived_sources_stay_out_of_current_legal_context(client) -> None:
    create_source(
        client,
        "Article 1. shared cable tax phrase belongs to a future draft source.",
        title="Future draft Tax Code",
        document_number="ZRU-FUTURE",
        status="draft",
        revision_date="2026-06-29",
    )
    create_source(
        client,
        "Article 1. shared cable tax phrase belongs to an outdated source.",
        title="Outdated Tax Code",
        document_number="ZRU-OLD",
        status="outdated",
        revision_date="2026-03-17",
    )
    create_source(
        client,
        "Article 1. shared cable tax phrase belongs to an archived source.",
        title="Archived Tax Code",
        document_number="ZRU-ARCHIVE",
        status="archived",
        revision_date="2025-12-31",
    )
    active = create_source(
        client,
        "Article 1. shared cable tax phrase belongs to the active current source.",
        title="Active Current Tax Code",
        document_number="ZRU-ACTIVE",
        revision_date="2026-03-17",
    )
    payload = legal_payload(
        {
            "source_type": "law",
            "legal_source_id": active["id"],
            "title": "Active Current Tax Code",
            "document_type": "cabinet_resolution",
            "document_number": "ZRU-ACTIVE",
            "revision_date": "2026-03-17",
            "article_or_point": "unknown",
            "source_name": "LEX.UZ",
            "source_url": "https://lex.uz/docs/999",
            "quote": "shared cable tax phrase belongs to the active current source.",
            "verification_status": "pending",
        }
    )
    gateway = Stage7Gateway(payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Version policy"}).json()["id"]
    client.post(
        f"/api/chats/{chat_id}/messages",
        json={"content": "shared cable tax phrase"},
    )

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    context = gateway.calls[0][1]
    assert "<TRUSTED_LEGAL_SOURCE" in context
    assert "<FUTURE_LEGAL_SOURCE" not in context
    assert "Active Current Tax Code" in context
    assert "Future draft Tax Code" not in context
    assert "Outdated Tax Code" not in context
    assert "Archived Tax Code" not in context
    assert response.json()["source_check_status"] == "not_checked"


def test_uploaded_documents_remain_untrusted_not_trusted_legal_sources(client) -> None:
    payload = legal_payload(
        {
            "source_type": "uploaded_document",
            "document_id": 1,
            "title": "contract.txt",
            "quote": "Поставка кабеля выполняется в июне.",
            "verification_status": "pending",
        }
    )
    gateway = Stage7Gateway(payload)
    app.dependency_overrides[get_llm_gateway] = lambda: gateway
    chat_id = client.post("/api/chats", json={"title": "Uploaded doc separation"}).json()["id"]
    upload = client.post(
        "/api/documents/upload",
        data={"chat_id": str(chat_id), "sensitivity": "internal"},
        files={"file": ("contract.txt", "Поставка кабеля выполняется в июне.".encode("utf-8"), "text/plain")},
    )
    assert upload.status_code == 201
    client.post(f"/api/chats/{chat_id}/messages", json={"content": "Проверь поставку"})

    response = client.post(f"/api/chats/{chat_id}/invoke", json={"agent_code": "lawyer_1"})

    assert response.status_code == 200
    context = gateway.calls[0][1]
    assert "<UNTRUSTED_DOCUMENT" in context
    assert "<TRUSTED_LEGAL_SOURCE" not in context
