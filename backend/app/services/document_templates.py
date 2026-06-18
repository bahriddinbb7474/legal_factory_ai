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
            "Напоминаем, что по основанию: {{ payment_basis }}\n"
            "Договор: № {{ contract.number }} от {{ contract.date }}\n"
            "Спецификация/счёт №: {{ invoice_or_spec_number }}\n\n"
            "За Вашей компанией числится задолженность в размере {{ debt.amount }} {{ debt.currency }}.\n"
            "Срок оплаты: {{ due_date }}.\n"
            "Дней просрочки: {{ overdue_days }}\n\n"
            "Просим произвести оплату в срок до: {{ requested_payment_deadline }}.\n\n"
            "Дополнительно сообщаем: {{ additional_note }}\n\n"
            "{{ document.body }}\n\n"
            "{{ bank_details_note }}\n"
            "{{ attached_documents_note }}\n\n"
            "Ответственный сотрудник: {{ responsible_person }}\n\n"
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
            "По основанию: {{ payment_basis }} (Договор № {{ contract.number }} от {{ contract.date }}, счёт/спецификация № {{ invoice_or_spec_number }})\n"
            "за Вами числится просроченная задолженность.\n\n"
            "По активному вердикту: {{ verdict.summary }}.\n"
            "Риск: {{ verdict.risk }}.\n\n"
            "Требуем оплатить задолженность в размере {{ debt.amount }} {{ debt.currency }}.\n"
            "Срок оплаты истек: {{ due_date }} (просрочка: {{ overdue_days }} дней).\n\n"
            "Срок для добровольной оплаты по претензии: {{ requested_payment_deadline }}.\n"
            "В случае неоплаты мы будем вынуждены обратиться в суд с взысканием суммы долга, а также пеней и судебных расходов.\n\n"
            "{{ additional_note }}\n\n"
            "{{ document.body }}\n\n"
            "Дополнительные действия: {{ verdict.actions }}\n\n"
            "{{ bank_details_note }}\n"
            "{{ attached_documents_note }}\n\n"
            "Ответственный сотрудник: {{ responsible_person }}\n"
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
    "contract.number",
    "contract.date",
    "invoice_or_spec_number",
    "debt.amount",
    "debt.currency",
    "due_date",
    "overdue_days",
    "payment_basis",
    "requested_payment_deadline",
    "responsible_person",
    "additional_note",
    "bank_details_note",
    "attached_documents_note",
    "amount",
    "today",
}


class DocumentTemplateService:
    async def ensure_default_templates(self, db: AsyncSession) -> None:
        result = await db.execute(select(DocumentTemplate).where(DocumentTemplate.template_key.in_([seed.template_key for seed in DEFAULT_DOCUMENT_TEMPLATES])))
        existing_templates = {t.template_key: t for t in result.scalars().all()}
        
        changed = False
        for seed in DEFAULT_DOCUMENT_TEMPLATES:
            if seed.template_key in existing_templates:
                t = existing_templates[seed.template_key]
                if (
                    t.name != seed.name
                    or t.description != seed.description
                    or t.body_template != seed.body_template
                    or t.category != seed.category
                ):
                    t.name = seed.name
                    t.description = seed.description
                    t.body_template = seed.body_template
                    t.category = seed.category
                    changed = True
            else:
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
        debt_amount: str | None = None,
        currency: str | None = None,
        payment_basis: str | None = None,
        contract_number: str | None = None,
        contract_date: str | None = None,
        invoice_or_spec_number: str | None = None,
        due_date: str | None = None,
        overdue_days: str | None = None,
        requested_payment_deadline: str | None = None,
        responsible_person: str | None = None,
        additional_note: str | None = None,
        bank_details_note: str | None = None,
        attached_documents_note: str | None = None,
        amount: str | None = None, # For backward compatibility
    ) -> dict[str, Any]:
        structured_payload = verdict.structured_payload if verdict and isinstance(verdict.structured_payload, dict) else {}
        actions = structured_payload.get("actions") if isinstance(structured_payload, dict) else None
        
        final_amount = debt_amount if debt_amount is not None else amount

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
            "contract": {
                "number": contract_number,
                "date": contract_date,
            },
            "debt": {
                "amount": final_amount,
                "currency": currency,
            },
            "invoice_or_spec_number": invoice_or_spec_number,
            "payment_basis": payment_basis,
            "due_date": due_date,
            "overdue_days": overdue_days,
            "requested_payment_deadline": requested_payment_deadline,
            "responsible_person": responsible_person,
            "additional_note": additional_note,
            "bank_details_note": bank_details_note,
            "attached_documents_note": attached_documents_note,
            "amount": final_amount,
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
