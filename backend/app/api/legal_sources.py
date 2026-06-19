from datetime import datetime, timedelta
from pathlib import Path

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import LegalChunk, LegalSource
from app.db.session import get_db
from app.schemas.legal_sources import (
    DOCUMENT_TYPES,
    OFFICIAL_STATUSES,
    SOURCE_STATUSES,
    LegalChunkInspectionRead,
    LegalChunkRead,
    LegalSourceDetailRead,
    LegalSourceRead,
    LegalSourceUpdate,
)
from app.services.audit import write_audit_log
from app.services.current_user import CurrentUser, get_current_user, require_role
from app.services.legal_chunker import legal_chunker
from app.storage.local import local_storage


router = APIRouter(prefix="/api/admin/legal-sources", tags=["admin-legal-sources"], dependencies=[Depends(require_role("admin"))])


@router.post("", response_model=LegalSourceDetailRead, status_code=status.HTTP_201_CREATED)
async def create_legal_source(
    document_type: str = Form(...),
    title: str = Form(...),
    source_name: str = Form(...),
    document_number: str | None = Form(default=None),
    source_url: str | None = Form(default=None),
    adoption_date: str | None = Form(default=None),
    revision_date: str | None = Form(default=None),
    language: str = Form(default="ru"),
    status_value: str = Form(default="active", alias="status"),
    official_status: str = Form(default="official"),
    raw_text: str | None = Form(default=None),
    file: UploadFile | None = File(default=None),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> LegalSourceDetailRead:
    _validate_metadata(document_type, status_value, official_status, title, source_name)
    content = await _read_source_content(raw_text, file)
    storage_key = await local_storage.save_text(content, suffix=".txt")
    now = datetime.utcnow()
    source = LegalSource(
        document_type=document_type,
        title=title.strip(),
        document_number=_clean_optional(document_number),
        source_name=source_name.strip(),
        source_url=_clean_optional(source_url),
        adoption_date=_clean_optional(adoption_date),
        revision_date=_clean_optional(revision_date),
        last_checked_at=now,
        next_check_due_at=now + timedelta(days=30),
        language=language.strip() or "ru",
        status=status_value,
        official_status=official_status,
        uploaded_by_user_id=current_user.id,
        storage_key=storage_key,
    )
    db.add(source)
    await db.flush()
    await _reindex_source(db, source, content)
    await write_audit_log(
        db,
        action="legal_source.created",
        entity_type="legal_source",
        entity_id=source.id,
        user_id=current_user.id,
        details={"document_type": source.document_type, "official_status": source.official_status},
    )
    await db.commit()
    return await _serialize_detail(source.id, db)


@router.get("", response_model=list[LegalSourceRead])
async def list_legal_sources(db: AsyncSession = Depends(get_db)) -> list[LegalSourceRead]:
    result = await db.execute(select(LegalSource).order_by(LegalSource.created_at.desc(), LegalSource.id.desc()))
    return [await _serialize_summary(source, db) for source in result.scalars().all()]


@router.get("/{source_id}", response_model=LegalSourceDetailRead)
async def get_legal_source(source_id: int, db: AsyncSession = Depends(get_db)) -> LegalSourceDetailRead:
    await _get_source_or_404(source_id, db)
    return await _serialize_detail(source_id, db)


@router.get("/{source_id}/chunks", response_model=list[LegalChunkInspectionRead])
async def list_legal_source_chunks(source_id: int, db: AsyncSession = Depends(get_db)) -> list[LegalChunkInspectionRead]:
    await _get_source_or_404(source_id, db)
    result = await db.execute(select(LegalChunk).where(LegalChunk.legal_source_id == source_id).order_by(LegalChunk.chunk_index))
    return [_serialize_chunk_inspection(chunk) for chunk in result.scalars().all()]


@router.patch("/{source_id}", response_model=LegalSourceRead)
async def update_legal_source(
    source_id: int,
    payload: LegalSourceUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> LegalSourceRead:
    source = await _get_source_or_404(source_id, db)
    updates = payload.model_dump(exclude_unset=True)
    if "document_type" in updates and updates["document_type"] not in DOCUMENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported legal document type")
    if "status" in updates and updates["status"] not in SOURCE_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported legal source status")
    if "official_status" in updates and updates["official_status"] not in OFFICIAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported official status")
    for field, value in updates.items():
        setattr(source, field, value)
    await write_audit_log(
        db,
        action="legal_source.updated",
        entity_type="legal_source",
        entity_id=source.id,
        user_id=current_user.id,
        details={"changed_fields": sorted(updates.keys())},
    )
    await db.commit()
    await db.refresh(source)
    return await _serialize_summary(source, db)


@router.delete("/{source_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_legal_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> None:
    source = await _get_source_or_404(source_id, db)
    await local_storage.delete(source.storage_key)
    await db.delete(source)
    await write_audit_log(db, action="legal_source.deleted", entity_type="legal_source", entity_id=source_id, user_id=current_user.id)
    await db.commit()


@router.post("/{source_id}/reindex", response_model=LegalSourceDetailRead)
async def reindex_legal_source(
    source_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> LegalSourceDetailRead:
    source = await _get_source_or_404(source_id, db)
    content = await local_storage.read_text(source.storage_key)
    await _reindex_source(db, source, content)
    source.last_checked_at = datetime.utcnow()
    source.next_check_due_at = source.last_checked_at + timedelta(days=30)
    await write_audit_log(db, action="legal_source.reindexed", entity_type="legal_source", entity_id=source.id, user_id=current_user.id)
    await db.commit()
    return await _serialize_detail(source.id, db)


async def _read_source_content(raw_text: str | None, file: UploadFile | None) -> str:
    if raw_text and raw_text.strip():
        return raw_text.strip()
    if file is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="file or raw_text is required")
    filename = Path(file.filename or "source.txt").name
    if filename != (file.filename or filename) or "\\" in (file.filename or "") or ".." in Path(file.filename or "").parts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    content = await file.read()
    try:
        return content.decode("utf-8").strip()
    except UnicodeDecodeError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Legal source text file must be UTF-8") from exc


async def _reindex_source(db: AsyncSession, source: LegalSource, content: str) -> None:
    await db.execute(delete(LegalChunk).where(LegalChunk.legal_source_id == source.id))
    for candidate in legal_chunker.chunk(content):
        db.add(
            LegalChunk(
                legal_source_id=source.id,
                article_or_point=candidate.article_or_point,
                section_title=candidate.section_title,
                chunk_index=candidate.chunk_index,
                chunk_text=candidate.chunk_text,
                embedding=None,
                metadata_json=candidate.metadata_json,
            )
        )
    await db.flush()


async def _serialize_detail(source_id: int, db: AsyncSession) -> LegalSourceDetailRead:
    source = await _get_source_or_404(source_id, db)
    result = await db.execute(select(LegalChunk).where(LegalChunk.legal_source_id == source_id).order_by(LegalChunk.chunk_index))
    chunks = list(result.scalars().all())
    summary = await _serialize_summary(source, db)
    return LegalSourceDetailRead(**summary.model_dump(), chunks=[LegalChunkRead.model_validate(chunk) for chunk in chunks])


async def _serialize_summary(source: LegalSource, db: AsyncSession) -> LegalSourceRead:
    count = await db.scalar(select(func.count(LegalChunk.id)).where(LegalChunk.legal_source_id == source.id))
    readiness_warnings = _readiness_warnings(source)
    readiness_warning_messages = [_READINESS_WARNING_MESSAGES[code] for code in readiness_warnings]
    revision_warning = None
    if "missing_revision_date" in readiness_warnings or "active_without_revision_date" in readiness_warnings:
        revision_warning = _READINESS_WARNING_MESSAGES["missing_revision_date"]
    elif "next_check_due_or_overdue" in readiness_warnings:
        revision_warning = _READINESS_WARNING_MESSAGES["next_check_due_or_overdue"]
    return LegalSourceRead(
        **{
            field: getattr(source, field)
            for field in [
                "id",
                "document_type",
                "title",
                "document_number",
                "source_name",
                "source_url",
                "adoption_date",
                "revision_date",
                "last_checked_at",
                "next_check_due_at",
                "language",
                "status",
                "official_status",
                "uploaded_by_user_id",
                "storage_key",
                "created_at",
                "updated_at",
            ]
        },
        chunks_count=int(count or 0),
        needs_revision_check=revision_warning is not None,
        revision_warning=revision_warning,
        readiness_warnings=readiness_warnings,
        readiness_warning_messages=readiness_warning_messages,
    )


def _serialize_chunk_inspection(chunk: LegalChunk) -> LegalChunkInspectionRead:
    preview = chunk.chunk_text.replace("\r\n", "\n").replace("\r", "\n").strip()
    preview = " ".join(preview.split())
    if len(preview) > 320:
        preview = f"{preview[:317]}..."
    return LegalChunkInspectionRead(
        id=chunk.id,
        chunk_index=chunk.chunk_index,
        article_or_point=chunk.article_or_point,
        section_title=chunk.section_title,
        text_preview=preview,
        chunk_text=chunk.chunk_text,
        char_count=len(chunk.chunk_text),
        created_at=chunk.created_at,
    )


async def _get_source_or_404(source_id: int, db: AsyncSession) -> LegalSource:
    source = await db.get(LegalSource, source_id)
    if source is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Legal source not found")
    return source


def _validate_metadata(document_type: str, source_status: str, official_status: str, title: str, source_name: str) -> None:
    if document_type not in DOCUMENT_TYPES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported legal document type")
    if source_status not in SOURCE_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported legal source status")
    if official_status not in OFFICIAL_STATUSES:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported official status")
    if not title.strip() or not source_name.strip():
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="title and source_name are required")


def _clean_optional(value: str | None) -> str | None:
    if value is None:
        return None
    cleaned = value.strip()
    return cleaned or None


def _readiness_warnings(source: LegalSource) -> list[str]:
    warnings: list[str] = []
    source_name = (source.source_name or "").strip()
    source_url = (source.source_url or "").strip()
    official_status = (source.official_status or "").strip()
    status_value = (source.status or "").strip()
    is_active = status_value == "active"
    is_official = official_status == "official"
    is_law_like = source.document_type in DOCUMENT_TYPES - {"other"}

    if not source_url:
        warnings.append("missing_source_url")
    if not source.document_number:
        warnings.append("missing_document_number")
    if not source.adoption_date:
        warnings.append("missing_adoption_date")
    if not source.revision_date:
        warnings.append("missing_revision_date")
    if not source_name:
        warnings.append("missing_source_name")
    if is_active and not is_official:
        warnings.append("active_without_official_status")
    if is_active and not source.revision_date:
        warnings.append("active_without_revision_date")
    if is_official and not source_url:
        warnings.append("official_source_without_url")
    if is_official and is_law_like and source_name.casefold() != "lex.uz":
        warnings.append("lexuz_expected_for_official_law")
    if source_name.casefold() == "lex.uz" and source_url and not _looks_like_lexuz_url(source_url):
        warnings.append("lexuz_source_with_bad_url")
    if not source.next_check_due_at or source.next_check_due_at < datetime.utcnow():
        warnings.append("next_check_due_or_overdue")

    return warnings


def _looks_like_lexuz_url(source_url: str) -> bool:
    normalized = source_url.casefold()
    return "lex.uz" in normalized or "lexuz" in normalized


_READINESS_WARNING_MESSAGES = {
    "missing_source_url": "Не указан официальный URL источника.",
    "missing_document_number": "Не указан номер документа.",
    "missing_adoption_date": "Не указана дата принятия.",
    "missing_revision_date": "Не указана дата редакции.",
    "missing_source_name": "Не указано имя источника.",
    "active_without_official_status": "Active source не помечен как official.",
    "active_without_revision_date": "Active source без даты редакции.",
    "official_source_without_url": "Official source без URL.",
    "lexuz_expected_for_official_law": "Для официального правового источника Stage 7 желательно использовать LEX.UZ.",
    "lexuz_source_with_bad_url": "Источник помечен как LEX.UZ, но URL не похож на lex.uz.",
    "next_check_due_or_overdue": "Следующая проверка редакции не задана или уже просрочена.",
}
