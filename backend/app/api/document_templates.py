from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.document_templates import DocumentTemplateRead
from app.services.document_templates import document_template_service


router = APIRouter(prefix="/api/document-templates", tags=["document-templates"])


@router.get("", response_model=list[DocumentTemplateRead])
async def list_document_templates(db: AsyncSession = Depends(get_db)) -> list[DocumentTemplateRead]:
    templates = await document_template_service.list_templates(db)
    return [DocumentTemplateRead.model_validate(template) for template in templates]


@router.get("/{template_key}", response_model=DocumentTemplateRead)
async def get_document_template(template_key: str, db: AsyncSession = Depends(get_db)) -> DocumentTemplateRead:
    template = await document_template_service.get_template(template_key, db)
    if template is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document template not found")
    return DocumentTemplateRead.model_validate(template)
