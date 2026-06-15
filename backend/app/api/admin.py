from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent, ProviderConfig
from app.db.session import get_db
from app.schemas.agents import AgentRead, AgentUpdate
from app.schemas.openrouter import OpenRouterModelRead
from app.schemas.providers import ProviderRead, ProviderUpdate
from app.services.agent_seed import LAWYER_PROVIDER_ERROR, ensure_default_config, validate_distinct_lawyer_providers
from app.services.openrouter_models import openrouter_model_service


router = APIRouter(prefix="/api/admin", tags=["admin"])


@router.get("/agents", response_model=list[AgentRead])
async def list_admin_agents(db: AsyncSession = Depends(get_db)) -> list[Agent]:
    await ensure_default_config(db)
    result = await db.execute(select(Agent).order_by(Agent.id))
    return list(result.scalars().all())


@router.patch("/agents/{agent_code}", response_model=AgentRead)
async def update_admin_agent(
    agent_code: str,
    payload: AgentUpdate,
    db: AsyncSession = Depends(get_db),
) -> Agent:
    await ensure_default_config(db)
    agent = await _get_agent_or_404(agent_code, db)
    previous_provider = agent.provider_code

    update_data = payload.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(agent, field, value)

    try:
        await validate_distinct_lawyer_providers(db)
    except ValueError as exc:
        agent.provider_code = previous_provider
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=LAWYER_PROVIDER_ERROR) from exc

    provider = await _get_provider_or_404(agent.provider_code, db)
    if not provider.is_enabled or not provider.is_allowlisted:
        await db.rollback()
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider is not allowlisted")

    await db.commit()
    await db.refresh(agent)
    return agent


@router.get("/providers", response_model=list[ProviderRead])
async def list_admin_providers(db: AsyncSession = Depends(get_db)) -> list[ProviderConfig]:
    await ensure_default_config(db)
    result = await db.execute(select(ProviderConfig).order_by(ProviderConfig.display_name))
    return list(result.scalars().all())


@router.patch("/providers/{provider_code}", response_model=ProviderRead)
async def update_admin_provider(
    provider_code: str,
    payload: ProviderUpdate,
    db: AsyncSession = Depends(get_db),
) -> ProviderConfig:
    await ensure_default_config(db)
    provider = await _get_provider_or_404(provider_code, db)
    for field, value in payload.model_dump(exclude_unset=True).items():
        setattr(provider, field, value)
    await db.commit()
    await db.refresh(provider)
    return provider


@router.get("/openrouter/models", response_model=list[OpenRouterModelRead])
async def list_openrouter_models() -> list[OpenRouterModelRead]:
    try:
        return await openrouter_model_service.list_models()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenRouter model list unavailable") from exc


@router.post("/openrouter/models/refresh", response_model=list[OpenRouterModelRead])
async def refresh_openrouter_models() -> list[OpenRouterModelRead]:
    try:
        return await openrouter_model_service.list_models(refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenRouter model list unavailable") from exc


async def _get_agent_or_404(agent_code: str, db: AsyncSession) -> Agent:
    result = await db.execute(select(Agent).where(Agent.code == agent_code))
    agent = result.scalar_one_or_none()
    if agent is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Lawyer not found")
    return agent


async def _get_provider_or_404(provider_code: str, db: AsyncSession) -> ProviderConfig:
    result = await db.execute(select(ProviderConfig).where(ProviderConfig.provider_code == provider_code))
    provider = result.scalar_one_or_none()
    if provider is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Provider not found")
    return provider
