from dataclasses import dataclass, field

from app.api.chats import get_llm_gateway
from app.main import app
from app.services.document_templates import document_template_service
from app.services.llm_gateway import LLMResponse


@dataclass
class TemplateGateway:
    calls: list[tuple[str, str]] = field(default_factory=list)
    content: str = "Основание задолженности подтверждено активным вердиктом."

    async def invoke(self, agent, chat_context: str, response_format: dict | None = None) -> LLMResponse:
        self.calls.append((agent.code, chat_context))
        return LLMResponse(
            content=self.content,
            model_id=agent.model_name,
            provider_code=agent.provider_code,
            input_tokens=5,
            output_tokens=10,
        )


def _create_chat(client) -> int:
    return client.post("/api/chats", json={"title": "Templates"}).json()["id"]


def _create_message(client, chat_id: int, content: str) -> dict:
    response = client.post(
        f"/api/chats/{chat_id}/messages",
        json={"author_type": "agent1", "content": content, "risk": "yellow", "approval_required": "none", "structured_payload": {"summary": "Нужно взыскание долга", "risk": "yellow", "actions": ["направить письмо", "подготовить претензию"]}},
    )
    assert response.status_code == 201
    return response.json()


def _prepare_company_profile(client) -> None:
    response = client.put(
        "/api/company-profile",
        json={
            "full_name": "Kabel Tech Energy LLC",
            "short_name": "Kabel Tech Energy",
            "legal_address": "Tashkent, Legal street 1",
            "actual_address": "Tashkent, Factory street 7",
            "tax_id": "123456789",
            "oked": "27320",
            "bank_name": "National Bank",
            "bank_mfo": "01001",
            "bank_account": "20208000123456789012",
            "director_name": "Director Name",
            "chief_accountant_name": "Chief Accountant",
            "legal_responsible_name": "Legal Responsible",
            "phone": "+998901234567",
            "email": "legal@kte.uz",
            "website": "https://kte.uz",
            "is_active": True,
            "notes": "Stage 9-A",
        },
    )
    assert response.status_code == 200


def test_list_and_get_document_templates(client) -> None:
    listed = client.get("/api/document-templates")

    assert listed.status_code == 200
    template_keys = [item["template_key"] for item in listed.json()]
    assert "client_debt_reminder" in template_keys
    assert "client_debt_claim" in template_keys

    template = client.get("/api/document-templates/client_debt_claim")

    assert template.status_code == 200
    assert template.json()["name"] == "Претензия клиенту о задолженности"


def test_generate_document_with_reminder_template_uses_company_profile_context(client) -> None:
    _prepare_company_profile(client)
    chat_id = _create_chat(client)
    verdict = _create_message(client, chat_id, "Нужно уведомить клиента о задолженности.")
    assert client.post(f"/api/chats/{chat_id}/messages/{verdict['id']}/mark-verdict").status_code == 200
    gateway = TemplateGateway()
    app.dependency_overrides[get_llm_gateway] = lambda: gateway

    response = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={
            "agent_code": "lawyer_1",
            "document_type": "client_debt_reminder",
            "title": "Письмо клиенту о задолженности",
            "template_key": "client_debt_reminder",
        },
    )

    assert response.status_code == 201
    payload = response.json()
    assert payload["template_key"] == "client_debt_reminder"
    assert "Kabel Tech Energy LLC" in payload["content"]
    assert "Основание задолженности подтверждено активным вердиктом." in payload["content"]
    assert "stamp" not in payload["content"].lower()
    assert "signature" not in payload["content"].lower()


def test_apply_claim_template_to_generated_document_without_real_assets(client) -> None:
    _prepare_company_profile(client)
    chat_id = _create_chat(client)
    verdict = _create_message(client, chat_id, "Нужно направить претензию.")
    assert client.post(f"/api/chats/{chat_id}/messages/{verdict['id']}/mark-verdict").status_code == 200
    gateway = TemplateGateway(content="Базовый черновик претензии.")
    app.dependency_overrides[get_llm_gateway] = lambda: gateway

    document = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={"agent_code": "lawyer_1", "document_type": "claim_letter", "title": "Черновик"},
    ).json()

    applied = client.post(
        f"/api/generated-documents/{document['id']}/apply-template",
        json={
            "template_key": "client_debt_claim",
            "counterparty_name": "ООО Должник",
            "debt_amount": "1000000",
            "currency": "UZS",
            "payment_basis": "Договор",
            "overdue_days": "15" # optional field
        },
    )

    assert applied.status_code == 200
    payload = applied.json()
    assert payload["document"]["template_key"] == "client_debt_claim"
    assert "Kabel Tech Energy LLC" in payload["document"]["content"]
    assert "Базовый черновик претензии." in payload["document"]["content"]
    assert "ООО Должник" in payload["document"]["content"]
    assert "1000000" in payload["document"]["content"]
    assert "15" in payload["document"]["content"] # optional field rendered
    assert "stamp" not in payload["document"]["content"].lower()
    assert "signature" not in payload["document"]["content"].lower()

def test_apply_debt_template_missing_required_fields_fails(client) -> None:
    _prepare_company_profile(client)
    chat_id = _create_chat(client)
    verdict = _create_message(client, chat_id, "Нужно направить претензию.")
    assert client.post(f"/api/chats/{chat_id}/messages/{verdict['id']}/mark-verdict").status_code == 200
    gateway = TemplateGateway(content="Базовый черновик претензии.")
    app.dependency_overrides[get_llm_gateway] = lambda: gateway

    document = client.post(
        f"/api/chats/{chat_id}/documents/generate-from-verdict",
        json={"agent_code": "lawyer_1", "document_type": "claim_letter", "title": "Черновик"},
    ).json()

    applied = client.post(
        f"/api/generated-documents/{document['id']}/apply-template",
        json={
            "template_key": "client_debt_claim",
            # Missing counterparty_name, debt_amount, currency, payment_basis
        },
    )

    assert applied.status_code == 422
    assert "Missing required fields" in applied.json()["detail"]
    assert "counterparty_name" in applied.json()["detail"]
    assert "debt_amount" in applied.json()["detail"]
    assert "currency" in applied.json()["detail"]
    assert "payment_basis" in applied.json()["detail"]


def test_unknown_placeholders_do_not_execute_code() -> None:
    rendered = document_template_service.render(
        "Hello {{ company.full_name }} {{ unknown.value }} {{ __import__.os }}",
        {"company": {"full_name": "KTE"}},
    )

    assert rendered.content == "Hello KTE  "
    assert "unknown.value" in rendered.missing_placeholders
    assert "__import__.os" in rendered.missing_placeholders


def test_company_profile_context_still_excludes_stamp_and_signature(client) -> None:
    _prepare_company_profile(client)

    # The HTTP API already stores the safe profile; verify the serialized response has no blocked keys.
    payload = client.get("/api/company-profile").json()
    assert "stamp" not in payload
    assert "signature" not in payload
