import mimetypes
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.db.session import get_db
from app.schemas.company_profile import CompanyProfileRead, CompanyProfileUpdate
from app.services.audit import write_audit_log
from app.services.company_profile import company_profile_service
from app.services.current_user import CurrentUser, get_current_user
from app.storage.local import local_storage


router = APIRouter(prefix="/api/company-profile", tags=["company-profile"])

LOGO_ALLOWED_EXTENSIONS = {
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
    ".webp": "image/webp",
}
LETTERHEAD_ALLOWED_EXTENSIONS = {
    ".doc": "application/msword",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
    ".pdf": "application/pdf",
    ".png": "image/png",
    ".jpg": "image/jpeg",
    ".jpeg": "image/jpeg",
}


@router.get("", response_model=CompanyProfileRead)
async def get_company_profile(db: AsyncSession = Depends(get_db)) -> CompanyProfileRead:
    profile = await company_profile_service.get_profile(db)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return CompanyProfileRead.model_validate(profile)


@router.put("", response_model=CompanyProfileRead)
async def put_company_profile(
    payload: CompanyProfileUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CompanyProfileRead:
    existing = await company_profile_service.get_profile(db)
    profile = await company_profile_service.upsert_profile(db, payload)
    await write_audit_log(
        db,
        action="company_profile.updated" if existing is not None else "company_profile.created",
        entity_type="company_profile",
        entity_id=profile.id,
        user_id=current_user.id,
        details={"is_active": profile.is_active},
    )
    await db.commit()
    await db.refresh(profile)
    return CompanyProfileRead.model_validate(profile)


@router.post("/logo", response_model=CompanyProfileRead)
async def upload_company_profile_logo(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CompanyProfileRead:
    profile = await _get_company_profile_or_404(db)
    content, suffix, mime_type, original_filename = await _read_asset_upload(file, LOGO_ALLOWED_EXTENSIONS)
    old_key = profile.logo_storage_key
    profile.logo_storage_key = await local_storage.save(content, suffix)
    if old_key and old_key != profile.logo_storage_key:
        await local_storage.delete(old_key)
    await write_audit_log(
        db,
        action="company_profile.logo_uploaded",
        entity_type="company_profile",
        entity_id=profile.id,
        user_id=current_user.id,
        details={"filename": original_filename, "mime_type": mime_type, "file_size": len(content)},
    )
    await db.commit()
    await db.refresh(profile)
    return CompanyProfileRead.model_validate(profile)


@router.delete("/logo", response_model=CompanyProfileRead)
async def delete_company_profile_logo(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CompanyProfileRead:
    profile = await _get_company_profile_or_404(db)
    if profile.logo_storage_key:
        await local_storage.delete(profile.logo_storage_key)
        profile.logo_storage_key = None
    await write_audit_log(
        db,
        action="company_profile.logo_deleted",
        entity_type="company_profile",
        entity_id=profile.id,
        user_id=current_user.id,
    )
    await db.commit()
    await db.refresh(profile)
    return CompanyProfileRead.model_validate(profile)


@router.post("/letterhead", response_model=CompanyProfileRead)
async def upload_company_profile_letterhead(
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CompanyProfileRead:
    profile = await _get_company_profile_or_404(db)
    content, suffix, mime_type, original_filename = await _read_asset_upload(file, LETTERHEAD_ALLOWED_EXTENSIONS)
    old_key = profile.letterhead_storage_key
    profile.letterhead_storage_key = await local_storage.save(content, suffix)
    if old_key and old_key != profile.letterhead_storage_key:
        await local_storage.delete(old_key)
    await write_audit_log(
        db,
        action="company_profile.letterhead_uploaded",
        entity_type="company_profile",
        entity_id=profile.id,
        user_id=current_user.id,
        details={"filename": original_filename, "mime_type": mime_type, "file_size": len(content)},
    )
    await db.commit()
    await db.refresh(profile)
    return CompanyProfileRead.model_validate(profile)


@router.delete("/letterhead", response_model=CompanyProfileRead)
async def delete_company_profile_letterhead(
    db: AsyncSession = Depends(get_db),
    current_user: CurrentUser = Depends(get_current_user),
) -> CompanyProfileRead:
    profile = await _get_company_profile_or_404(db)
    if profile.letterhead_storage_key:
        await local_storage.delete(profile.letterhead_storage_key)
        profile.letterhead_storage_key = None
    await write_audit_log(
        db,
        action="company_profile.letterhead_deleted",
        entity_type="company_profile",
        entity_id=profile.id,
        user_id=current_user.id,
    )
    await db.commit()
    await db.refresh(profile)
    return CompanyProfileRead.model_validate(profile)


async def _get_company_profile_or_404(db: AsyncSession):
    profile = await company_profile_service.get_profile(db)
    if profile is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Company profile not found")
    return profile


async def _read_asset_upload(
    file: UploadFile,
    allowed_extensions: dict[str, str],
) -> tuple[bytes, str, str, str]:
    raw_filename = file.filename or "asset"
    original_filename = Path(raw_filename).name
    if original_filename != raw_filename or "\\" in raw_filename or ".." in Path(raw_filename).parts:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Invalid file name")
    suffix = Path(original_filename).suffix.lower()
    if suffix not in allowed_extensions:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Unsupported file type")
    content = await file.read()
    if not content:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Empty file is not allowed")
    max_size = settings.max_upload_size_mb * 1024 * 1024
    if len(content) > max_size:
        raise HTTPException(status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE, detail="Upload size limit exceeded")
    mime_type = _resolve_mime_type(file.content_type, suffix, allowed_extensions)
    return content, suffix, mime_type, original_filename


def _resolve_mime_type(content_type: str | None, suffix: str, allowed_extensions: dict[str, str]) -> str:
    expected = allowed_extensions[suffix]
    guessed = content_type or mimetypes.types_map.get(suffix) or expected
    if guessed == "application/octet-stream":
        return expected
    if guessed != expected:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File MIME type does not match extension")
    return expected
