from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.schemas.generated_documents import GeneratedDocumentRead


class DocumentTemplateRead(BaseModel):
    id: int
    template_key: str
    name: str
    description: str
    category: str
    language: str
    template_type: str
    body_template: str
    docx_template_storage_key: str | None = None
    is_active: bool
    requires_approval: bool
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class ApplyDocumentTemplateRequest(BaseModel):
    template_key: str
    counterparty_name: str | None = None
    counterparty_address: str | None = None
    counterparty_tax_id: str | None = None
    debt_amount: str | None = None
    currency: str | None = None
    payment_basis: str | None = None
    contract_number: str | None = None
    contract_date: str | None = None
    invoice_or_spec_number: str | None = None
    due_date: str | None = None
    overdue_days: str | None = None
    requested_payment_deadline: str | None = None
    responsible_person: str | None = None
    additional_note: str | None = None
    bank_details_note: str | None = None
    attached_documents_note: str | None = None
    # Backward compatibility
    amount: str | None = None


class ApplyDocumentTemplateResponse(BaseModel):
    document: GeneratedDocumentRead
    missing_placeholders: list[str] = Field(default_factory=list)
