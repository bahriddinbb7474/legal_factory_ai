from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Response, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Approval, GeneratedDocument, Message
from app.db.session import get_db
from app.schemas.approvals import ApprovalRead
from app.schemas.document_templates import ApplyDocumentTemplateRequest, ApplyDocumentTemplateResponse
from app.schemas.generated_documents import (
    GeneratedDocumentRead,
    GeneratedDocumentUpdate,
    SendGeneratedDocumentToChatResponse,
)
from app.services.company_profile import get_company_profile_context
from app.services.audit import write_audit_log
from app.services.current_user import CurrentUser, get_current_user
from app.services.document_templates import document_template_service
from app.services.generated_documents import build_docx_export, build_pdf_export, save_generated_document_text


router = APIRouter(prefix="/api/generated-documents", tags=["generated-documents"])


@router.get("/{document_id}", response_model=GeneratedDocumentRead)
async def get_generated_document(document_id: int, db: AsyncSession = Depends(get_db)) -> GeneratedDocument:
    return await _get_generated_document_or_404(document_id, db)


@router.patch("/{document_id}", response_model=GeneratedDocumentRead)
async def update_generated_document(
    document_id: int,
    payload: GeneratedDocumentUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> GeneratedDocument:
    document = await _get_generated_document_or_404(document_id, db)
    updates = payload.model_dump(exclude_unset=True)
    previous_status = document.status
    if "title" in updates and updates["title"] is not None:
        document.title = updates["title"]
    if "content" in updates and updates["content"] is not None:
        document.content = updates["content"]
        document.storage_key = await save_generated_document_text(document.content)
        document.docx_storage_key = None
        document.pdf_storage_key = None
    if "status" in updates and updates["status"] is not None:
        document.status = updates["status"]
    await write_audit_log(
        db,
        action="generated_document.edited",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=current_user.id,
        details={"changed_fields": sorted(updates.keys()), "previous_status": previous_status, "new_status": document.status},
    )
    await db.commit()
    await db.refresh(document)
    return document


@router.get("/{document_id}/download.docx")
async def download_generated_document_docx(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Response:
    document = await _get_generated_document_or_404(document_id, db)
    data, storage_key = await build_docx_export(document.title, document.content)
    document.docx_storage_key = storage_key
    await write_audit_log(
        db,
        action="generated_document.exported_docx",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=current_user.id,
        details={"title": document.title, "storage_key": storage_key},
    )
    await db.commit()
    return Response(
        content=data,
        media_type="application/vnd.openxmlformats-officedocument.wordprocessingml.document",
        headers={"Content-Disposition": f'attachment; filename="generated-document-{document.id}.docx"'},
    )


@router.get("/{document_id}/download.pdf")
async def download_generated_document_pdf(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Response:
    document = await _get_generated_document_or_404(document_id, db)
    data, storage_key = await build_pdf_export(document.title, document.content)
    document.pdf_storage_key = storage_key
    await write_audit_log(
        db,
        action="generated_document.exported_pdf",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=current_user.id,
        details={"title": document.title, "storage_key": storage_key},
    )
    await db.commit()
    return Response(
        content=data,
        media_type="application/pdf",
        headers={"Content-Disposition": f'attachment; filename="generated-document-{document.id}.pdf"'},
    )


@router.post("/{document_id}/send-to-chat", response_model=SendGeneratedDocumentToChatResponse)
async def send_generated_document_to_chat(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> SendGeneratedDocumentToChatResponse:
    document = await _get_generated_document_or_404(document_id, db)
    message = Message(
        chat_id=document.chat_id,
        role="user",
        author_type="user",
        content=f"Документ отправлен в общий чат для дальнейшей проверки: {document.title}",
    )
    db.add(message)
    await db.flush()
    await write_audit_log(
        db,
        action="generated_document.sent_to_chat",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=current_user.id,
        details={"chat_id": document.chat_id, "message_id": message.id},
    )
    await db.commit()
    return SendGeneratedDocumentToChatResponse(message_id=message.id, document_id=document.id)


@router.post("/{document_id}/apply-template", response_model=ApplyDocumentTemplateResponse)
async def apply_document_template(
    document_id: int,
    payload: ApplyDocumentTemplateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ApplyDocumentTemplateResponse:
    document = await _get_generated_document_or_404(document_id, db)
    template = await document_template_service.get_template(payload.template_key, db)
    if template is None or not template.is_active:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found")
    if template.template_key in ("client_debt_reminder", "client_debt_claim"):
        missing_required = []
        if not payload.counterparty_name:
            missing_required.append("counterparty_name")
        if not payload.debt_amount and not payload.amount:
            missing_required.append("debt_amount")
        if not payload.currency:
            missing_required.append("currency")
        if not payload.payment_basis:
            missing_required.append("payment_basis")
        
        if missing_required:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Missing required fields for debt template: {', '.join(missing_required)}"
            )

    verdict = await document_template_service.get_verdict_message(document, db)
    company = await get_company_profile_context(db)
    render_context = document_template_service.build_render_context(
        company=company,
        document=document,
        verdict=verdict,
        counterparty_name=payload.counterparty_name,
        counterparty_address=payload.counterparty_address,
        counterparty_tax_id=payload.counterparty_tax_id,
        debt_amount=payload.debt_amount,
        currency=payload.currency,
        payment_basis=payload.payment_basis,
        contract_number=payload.contract_number,
        contract_date=payload.contract_date,
        invoice_or_spec_number=payload.invoice_or_spec_number,
        due_date=payload.due_date,
        overdue_days=payload.overdue_days,
        requested_payment_deadline=payload.requested_payment_deadline,
        responsible_person=payload.responsible_person,
        additional_note=payload.additional_note,
        bank_details_note=payload.bank_details_note,
        attached_documents_note=payload.attached_documents_note,
        amount=payload.amount,
    )
    rendered = document_template_service.render(template.body_template, render_context)
    document.content = rendered.content
    document.template_key = template.template_key
    document.storage_key = await save_generated_document_text(document.content)
    document.docx_storage_key = None
    document.pdf_storage_key = None
    await write_audit_log(
        db,
        action="generated_document.template_applied",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=current_user.id,
        details={"template_key": template.template_key, "missing_placeholders": rendered.missing_placeholders},
    )
    await db.commit()
    await db.refresh(document)
    return ApplyDocumentTemplateResponse(
        document=GeneratedDocumentRead.model_validate(document),
        missing_placeholders=rendered.missing_placeholders,
    )


@router.post("/{document_id}/request-approval", response_model=GeneratedDocumentRead)
async def request_generated_document_approval(
    document_id: int,
    comment: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> GeneratedDocument:
    document = await _get_generated_document_or_404(document_id, db)
    await _record_document_approval_event(db, document, "request", current_user, "needs_review", comment)
    await db.commit()
    await db.refresh(document)
    return document


@router.post("/{document_id}/approve", response_model=GeneratedDocumentRead)
async def approve_generated_document(
    document_id: int,
    comment: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> GeneratedDocument:
    _assert_can_approve(current_user)
    document = await _get_generated_document_or_404(document_id, db)
    await _record_document_approval_event(db, document, "approve", current_user, "approved", comment)
    await db.commit()
    await db.refresh(document)
    return document


@router.post("/{document_id}/reject", response_model=GeneratedDocumentRead)
async def reject_generated_document(
    document_id: int,
    comment: str | None = None,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> GeneratedDocument:
    _assert_can_approve(current_user)
    document = await _get_generated_document_or_404(document_id, db)
    await _record_document_approval_event(db, document, "reject", current_user, "rejected", comment)
    await db.commit()
    await db.refresh(document)
    return document


@router.get("/{document_id}/approvals", response_model=list[ApprovalRead])
async def list_generated_document_approvals(
    document_id: int,
    db: AsyncSession = Depends(get_db),
) -> list[Approval]:
    document = await _get_generated_document_or_404(document_id, db)
    result = await db.execute(
        select(Approval)
        .where(Approval.entity_type == "generated_document", Approval.entity_id == document.id)
        .order_by(Approval.performed_at, Approval.id)
    )
    return list(result.scalars().all())


async def _get_generated_document_or_404(document_id: int, db: AsyncSession) -> GeneratedDocument:
    document = await db.get(GeneratedDocument, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Generated document not found")
    return document


def _assert_can_approve(user: CurrentUser) -> None:
    if user.role not in {"director", "chief_accountant"}:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Only director or chief accountant can approve or reject.",
        )


async def _record_document_approval_event(
    db: AsyncSession,
    document: GeneratedDocument,
    action: str,
    user: CurrentUser,
    new_status: str,
    comment: str | None,
) -> None:
    previous_status = document.status
    document.status = new_status
    event = Approval(
        chat_id=document.chat_id,
        requested_by_user_id=user.id,
        approved_by_user_id=user.id if action in {"approve", "reject"} else None,
        status=new_status,
        comment=comment,
        entity_type="generated_document",
        entity_id=document.id,
        action=action,
        performed_by_user_id=user.id,
        performed_at=datetime.utcnow(),
        previous_status=previous_status,
        new_status=new_status,
    )
    db.add(event)
    await write_audit_log(
        db,
        action=f"generated_document.approval_{action}",
        entity_type="generated_document",
        entity_id=document.id,
        user_id=user.id,
        details={"previous_status": previous_status, "new_status": new_status},
    )
