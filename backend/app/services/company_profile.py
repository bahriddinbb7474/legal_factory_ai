from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import CompanyProfile
from app.schemas.company_profile import CompanyProfileContext, CompanyProfileUpdate


class CompanyProfileService:
    async def get_profile(self, db: AsyncSession) -> CompanyProfile | None:
        result = await db.execute(select(CompanyProfile).order_by(CompanyProfile.is_active.desc(), CompanyProfile.id.asc()))
        return result.scalars().first()

    async def upsert_profile(self, db: AsyncSession, payload: CompanyProfileUpdate) -> CompanyProfile:
        profile = await self.get_profile(db)
        if profile is None:
            profile = CompanyProfile()
            db.add(profile)

        for field, value in payload.model_dump().items():
            setattr(profile, field, value)

        if profile.is_active:
            await self._deactivate_other_profiles(db, profile.id)

        await db.flush()
        return profile

    async def get_profile_context(self, db: AsyncSession) -> CompanyProfileContext | None:
        profile = await self.get_profile(db)
        if profile is None or not profile.is_active:
            return None
        return CompanyProfileContext.model_validate(profile, from_attributes=True)

    async def _deactivate_other_profiles(self, db: AsyncSession, keep_id: int | None) -> None:
        result = await db.execute(select(CompanyProfile))
        for profile in result.scalars().all():
            if keep_id is not None and profile.id == keep_id:
                continue
            if profile.is_active:
                profile.is_active = False

    def context_dict(self, context: CompanyProfileContext | None) -> dict[str, Any]:
        if context is None:
            return {}
        return context.model_dump()


company_profile_service = CompanyProfileService()


async def get_company_profile_context(db: AsyncSession) -> CompanyProfileContext | None:
    return await company_profile_service.get_profile_context(db)
