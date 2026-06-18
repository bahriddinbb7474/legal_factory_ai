from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_db
from app.schemas.company_profile import CompanyProfileRead, CompanyProfileUpdate
from app.services.audit import write_audit_log
from app.services.company_profile import company_profile_service
from app.services.current_user import CurrentUser, get_current_user


router = APIRouter(prefix="/api/company-profile", tags=["company-profile"])


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
