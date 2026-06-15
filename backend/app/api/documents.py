import hashlib
import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from fastapi.responses import Response
from sqlalchemy import delete, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.base import Chat, ChatDocument, Document, MessageDocument
from app.db.session import get_db
from app.schemas.documents import ChatDocumentRead, DocumentContentRead, DocumentRead, DocumentUploadResponse
from app.services.audit import write_audit_log
from app.services.current_user import CurrentUser, get_current_user
from app.services.document_access import DocumentAccessError, document_access_service
from app.services.document_categories import DOCUMENT_CATEGORIES, suggest_category
from app.services.document_extractor import document_extractor
from app.storage.local import local_storage


router = APIRouter(prefix="/api/documents", tags=["documents"])
chat_router = APIRouter(prefix="/api/chats", tags=["chat-documents"])

ALLOWED_EXTENSIONS = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".xlsx": "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    ".txt": "text/plain",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".png": "image/png",
    ".webp": "image/webp",
}
ALLOWED_SENSITIVITY = {"normal", "internal", "sensitive"}


@router.post("/upload", response_model=DocumentUploadResponse, status_code=status.HTTP_201_CREATED)
async def upload_document(
    file: UploadFile = File(...),
    category: str | None = Form(default=None),
    sensitivity: str = Form(default="internal"),
    counterparty: str | None = Form(default=None),
    document_number: str | None = Form(default=None),
    document_date: str | None = Form(default=None),
    chat_id: int | None = Form(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> DocumentUploadResponse:
    raw_filename = file.filename or "document"
    original_filename = Path(raw_filename).name
    if original_filename != raw_filename or "\\" in raw_filename or ".." in Path(raw_filename).parts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    suffix = Path(original_filename).suffix.lower()
    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    if sensitivity not in ALLOWED_SENSITIVITY:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported sensitivity value")
    if category and category not in DOCUMENT_CATEGORIES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported document category")

    content = await file.read()
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Upload size limit exceeded")

    mime_type = _resolve_mime_type(file.content_type, suffix)
    file_hash = hashlib.sha256(content).hexdigest()
    existing_document = await _get_document_by_hash(file_hash, db)

    if existing_document is None:
        storage_key = await local_storage.save(content, suffix)
        extraction = await document_extractor.extract(content, mime_type, original_filename)
        text_storage_key = await local_storage.save_text(extraction.text) if extraction.text else None
        suggested = suggest_category(original_filename, extraction.text)
        document = Document(
            chat_id=chat_id,
            filename=original_filename,
            file_type=suffix.lstrip("."),
            storage_path=storage_key,
            original_filename=original_filename,
            storage_key=storage_key,
            mime_type=mime_type,
            file_size=len(content),
            file_hash=file_hash,
            category=category or suggested,
            suggested_category=suggested,
            counterparty=counterparty,
            document_number=document_number,
            document_date=document_date,
            sensitivity=sensitivity,
            uploaded_by_user_id=current_user.id,
            extraction_status=extraction.extraction_status,
            extracted_text_storage_key=text_storage_key,
            ocr_status=extraction.ocr_status,
            status="draft",
        )
        document_access_service.assert_can_access(current_user, document, "upload")
        db.add(document)
        await db.flush()
        extraction_error = extraction.error
    else:
        document = existing_document
        document_access_service.assert_can_access(current_user, document, "upload")
        extraction_error = None

    if chat_id is not None:
        await _get_chat_or_404(chat_id, db)
        await _link_document_to_chat(chat_id, document.id, current_user.id, db)

    await write_audit_log(
        db,
        action="document.upload",
        entity_type="document",
        entity_id=document.id,
        user_id=current_user.id,
        details={
            "filename": original_filename,
            "mime_type": mime_type,
            "file_size": len(content),
            "sensitivity": document.sensitivity,
            "extraction_status": document.extraction_status,
            "ocr_status": document.ocr_status,
        },
    )
    await db.commit()
    await db.refresh(document)
    return DocumentUploadResponse(document=document, extraction_error=extraction_error)


@router.get("", response_model=list[DocumentRead])
async def list_documents(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[Document]:
    result = await db.execute(select(Document).order_by(Document.created_at.desc(), Document.id.desc()))
    documents = list(result.scalars().all())
    return [document for document in documents if _can_access(current_user, document, "view")]


@router.get("/{document_id}", response_model=DocumentRead)
async def get_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Document:
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "view")
    await write_audit_log(db, action="document.open", entity_type="document", entity_id=document.id, user_id=current_user.id)
    await db.commit()
    return document


@router.get("/{document_id}/content", response_model=DocumentContentRead)
async def get_document_content(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> DocumentContentRead:
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "read extracted text")
    text = await _read_extracted_text(document)
    return DocumentContentRead(document=document, extracted_text=text)


@router.get("/{document_id}/download")
async def download_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> Response:
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "download")
    content = await local_storage.read(document.storage_key)
    await write_audit_log(db, action="document.download", entity_type="document", entity_id=document.id, user_id=current_user.id)
    await db.commit()
    return Response(
        content,
        media_type=document.mime_type,
        headers={"Content-Disposition": f'attachment; filename="{document.original_filename}"'},
    )


@router.delete("/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_document(
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "delete")
    await db.execute(delete(ChatDocument).where(ChatDocument.document_id == document_id))
    await db.execute(delete(MessageDocument).where(MessageDocument.document_id == document_id))
    await local_storage.delete(document.storage_key)
    if document.extracted_text_storage_key:
        await local_storage.delete(document.extracted_text_storage_key)
    await db.delete(document)
    await write_audit_log(db, action="document.delete", entity_type="document", entity_id=document_id, user_id=current_user.id)
    await db.commit()


@chat_router.post("/{chat_id}/documents/{document_id}", response_model=ChatDocumentRead)
async def link_chat_document(
    chat_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> ChatDocumentRead:
    await _get_chat_or_404(chat_id, db)
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "link")
    link = await _link_document_to_chat(chat_id, document_id, current_user.id, db)
    await write_audit_log(db, action="document.link_chat", entity_type="document", entity_id=document_id, user_id=current_user.id, details={"chat_id": chat_id})
    await db.commit()
    return ChatDocumentRead(chat_id=chat_id, document=document, created_at=link.created_at)


@chat_router.delete("/{chat_id}/documents/{document_id}", status_code=status.HTTP_204_NO_CONTENT)
async def unlink_chat_document(
    chat_id: int,
    document_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    document = await _get_document_or_404(document_id, db)
    _assert_access(current_user, document, "unlink")
    await db.execute(delete(ChatDocument).where(ChatDocument.chat_id == chat_id, ChatDocument.document_id == document_id))
    await write_audit_log(db, action="document.unlink_chat", entity_type="document", entity_id=document_id, user_id=current_user.id, details={"chat_id": chat_id})
    await db.commit()


@chat_router.get("/{chat_id}/documents", response_model=list[ChatDocumentRead])
async def list_chat_documents(
    chat_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> list[ChatDocumentRead]:
    await _get_chat_or_404(chat_id, db)
    result = await db.execute(
        select(ChatDocument, Document)
        .join(Document, Document.id == ChatDocument.document_id)
        .where(ChatDocument.chat_id == chat_id)
        .order_by(ChatDocument.created_at, ChatDocument.document_id)
    )
    response: list[ChatDocumentRead] = []
    for link, document in result.all():
        if _can_access(current_user, document, "view"):
            response.append(ChatDocumentRead(chat_id=chat_id, document=document, created_at=link.created_at))
    return response


async def _get_document_or_404(document_id: int, db: AsyncSession) -> Document:
    document = await db.get(Document, document_id)
    if document is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Document not found")
    return document


async def _get_document_by_hash(file_hash: str, db: AsyncSession) -> Document | None:
    result = await db.execute(select(Document).where(Document.file_hash == file_hash).order_by(Document.id))
    return result.scalars().first()


async def _get_chat_or_404(chat_id: int, db: AsyncSession) -> Chat:
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


async def _link_document_to_chat(chat_id: int, document_id: int, user_id: int, db: AsyncSession) -> ChatDocument:
    link = await db.get(ChatDocument, {"chat_id": chat_id, "document_id": document_id})
    if link is None:
        link = ChatDocument(chat_id=chat_id, document_id=document_id, added_by_user_id=user_id)
        db.add(link)
        await db.flush()
    return link


async def _read_extracted_text(document: Document) -> str:
    if document.extraction_status != "completed" or not document.extracted_text_storage_key:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Document text is not available")
    return await local_storage.read_text(document.extracted_text_storage_key)


def _resolve_mime_type(content_type: str | None, suffix: str) -> str:
    expected = ALLOWED_EXTENSIONS[suffix]
    guessed = content_type or mimetypes.types_map.get(suffix) or expected
    if guessed == "application/octet-stream":
        return expected
    if guessed != expected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File MIME type does not match extension")
    return expected


def _assert_access(user: CurrentUser, document: Document, action: str) -> None:
    try:
        document_access_service.assert_can_access(user, document, action)
    except DocumentAccessError as exc:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(exc)) from exc


def _can_access(user: CurrentUser, document: Document, action: str) -> bool:
    try:
        document_access_service.assert_can_access(user, document, action)
        return True
    except DocumentAccessError:
        return False
