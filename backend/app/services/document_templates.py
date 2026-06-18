import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import DocumentTemplate, GeneratedDocument, Message
from app.schemas.company_profile import CompanyProfileContext


@dataclass(frozen=True)
class TemplateSeed:
    template_key: str
    name: str
    description: str
    category: str
    body_template: str


@dataclass(frozen=True)
class RenderedTemplate:
    content: str
    missing_placeholders: list[str]


DEFAULT_DOCUMENT_TEMPLATES: tuple[TemplateSeed, ...] = (
    TemplateSeed(
        template_key="client_debt_reminder",
        name="Письмо клиенту о задолженности",
        description="Мягкое письмо-напоминание клиенту о необходимости оплатить задолженность.",
        category="debt",
        body_template=(
            "{{ company.full_name }}\n"
            "{{ company.legal_address }}\n"
            "ИНН: {{ company.tax_id }}\n"
            "Тел.: {{ company.phone }} | Email: {{ company.email }}\n\n"
            "Кому: {{ counterparty.name }}\n"
            "Адрес: {{ counterparty.address }}\n"
            "ИНН: {{ counterparty.tax_id }}\n\n"
            "Дата: {{ today }}\n\n"
            "Тема: Напоминание об оплате задолженности\n\n"
            "Уважаемые коллеги,\n\n"
            "По результатам внутренней проверки {{ verdict.summary }}.\n"
            "Просим оплатить задолженность в размере {{ amount }} до {{ due_date }}.\n\n"
            "{{ document.body }}\n\n"
            "С уважением,\n"
            "{{ company.director_name }}\n"
            "{{ company.short_name }}\n"
        ),
    ),
    TemplateSeed(
        template_key="client_debt_claim",
        name="Претензия клиенту о задолженности",
        description="Претензионное письмо клиенту о погашении задолженности.",
        category="claim",
        body_template=(
            "{{ company.full_name }}\n"
            "{{ company.legal_address }}\n"
            "Банк: {{ company.bank_name }}, МФО {{ company.bank_mfo }}, р/с {{ company.bank_account }}\n\n"
            "Кому: {{ counterparty.name }}\n"
            "Адрес: {{ counterparty.address }}\n"
            "ИНН: {{ counterparty.tax_id }}\n\n"
            "Дата: {{ today }}\n\n"
            "ПРЕТЕНЗИЯ\n\n"
            "По активному вердикту: {{ verdict.summary }}.\n"
            "Риск: {{ verdict.risk }}.\n"
            "Требуем оплатить задолженность в размере {{ amount }} не позднее {{ due_date }}.\n\n"
            "{{ document.body }}\n\n"
            "Дополнительные действия: {{ verdict.actions }}\n\n"
            "Контактное лицо: {{ company.legal_responsible_name }}, {{ company.phone }}, {{ company.email }}\n"
        ),
    ),
)

PLACEHOLDER_PATTERN = re.compile(r"{{\s*([a-zA-Z0-9_.]+)\s*}}")
ALLOWED_PLACEHOLDERS = {
    "company.full_name",
    "company.short_name",
    "company.legal_address",
    "company.actual_address",
    "company.tax_id",
    "company.oked",
    "company.bank_name",
    "company.bank_mfo",
    "company.bank_account",
    "company.director_name",
    "company.chief_accountant_name",
    "company.legal_responsible_name",
    "company.phone",
    "company.email",
    "company.website",
    "company.logo_storage_key",
    "company.letterhead_storage_key",
    "document.title",
    "document.body",
    "verdict.summary",
    "verdict.risk",
    "verdict.actions",
    "counterparty.name",
    "counterparty.address",
    "counterparty.tax_id",
    "amount",
    "due_date",
    "today",
}


class DocumentTemplateService:
    async def ensure_default_templates(self, db: AsyncSession) -> None:
        result = await db.execute(select(DocumentTemplate.template_key))
        existing = set(result.scalars().all())
        changed = False
        for seed in DEFAULT_DOCUMENT_TEMPLATES:
            if seed.template_key in existing:
                continue
            db.add(
                DocumentTemplate(
                    template_key=seed.template_key,
                    name=seed.name,
                    description=seed.description,
                    category=seed.category,
                    language="ru",
                    template_type="text_to_docx",
                    body_template=seed.body_template,
                    is_active=True,
                    requires_approval=False,
                )
            )
            changed = True
        if changed:
            await db.commit()

    async def list_templates(self, db: AsyncSession) -> list[DocumentTemplate]:
        await self.ensure_default_templates(db)
        result = await db.execute(select(DocumentTemplate).where(DocumentTemplate.is_active.is_(True)).order_by(DocumentTemplate.id))
        return list(result.scalars().all())

    async def get_template(self, template_key: str, db: AsyncSession) -> DocumentTemplate | None:
        await self.ensure_default_templates(db)
        result = await db.execute(select(DocumentTemplate).where(DocumentTemplate.template_key == template_key))
        return result.scalar_one_or_none()

    def render(self, body_template: str, context: dict[str, Any]) -> RenderedTemplate:
        missing: list[str] = []

        def replace(match: re.Match[str]) -> str:
            placeholder = match.group(1)
            if placeholder not in ALLOWED_PLACEHOLDERS:
                missing.append(placeholder)
                return ""
            value = self._resolve_placeholder(context, placeholder)
            if value is None or value == "":
                missing.append(placeholder)
                return ""
            if isinstance(value, list):
                return ", ".join(str(item) for item in value)
            return str(value)

        return RenderedTemplate(content=PLACEHOLDER_PATTERN.sub(replace, body_template), missing_placeholders=sorted(set(missing)))

    def build_render_context(
        self,
        *,
        company: CompanyProfileContext | None,
        document: GeneratedDocument,
        verdict: Message | None,
        counterparty_name: str | None = None,
        counterparty_address: str | None = None,
        counterparty_tax_id: str | None = None,
        amount: str | None = None,
        due_date: str | None = None,
    ) -> dict[str, Any]:
        structured_payload = verdict.structured_payload if verdict and isinstance(verdict.structured_payload, dict) else {}
        actions = structured_payload.get("actions") if isinstance(structured_payload, dict) else None
        return {
            "company": company.model_dump(mode="python") if company is not None else {},
            "document": {"title": document.title, "body": document.content},
            "verdict": {
                "summary": structured_payload.get("summary") or (verdict.content if verdict else ""),
                "risk": structured_payload.get("risk") or (verdict.risk if verdict else ""),
                "actions": actions or [],
            },
            "counterparty": {
                "name": counterparty_name,
                "address": counterparty_address,
                "tax_id": counterparty_tax_id,
            },
            "amount": amount,
            "due_date": due_date,
            "today": datetime.utcnow().date().isoformat(),
        }

    async def get_verdict_message(self, document: GeneratedDocument, db: AsyncSession) -> Message | None:
        return await db.get(Message, document.verdict_message_id)

    def _resolve_placeholder(self, context: dict[str, Any], placeholder: str) -> Any:
        value: Any = context
        for part in placeholder.split("."):
            if isinstance(value, dict):
                value = value.get(part)
            else:
                return None
        return value


document_template_service = DocumentTemplateService()
