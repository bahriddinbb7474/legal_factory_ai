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

    if "model_name" in update_data or "provider_code" in update_data:
        await _ensure_model_provider_config(agent.model_name, agent.provider_code, db)
        await _validate_openrouter_model_choice(agent.model_name, agent.provider_code)

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


@router.patch("/providers/{provider_code:path}", response_model=ProviderRead)
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
async def list_openrouter_models(db: AsyncSession = Depends(get_db)) -> list[OpenRouterModelRead]:
    try:
        models = await openrouter_model_service.list_models()
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenRouter model list unavailable") from exc
    await _ensure_model_providers(models, db)
    return models


@router.post("/openrouter/models/refresh", response_model=list[OpenRouterModelRead])
async def refresh_openrouter_models(db: AsyncSession = Depends(get_db)) -> list[OpenRouterModelRead]:
    try:
        models = await openrouter_model_service.list_models(refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenRouter model list unavailable") from exc
    await _ensure_model_providers(models, db)
    return models


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


async def _ensure_model_providers(models: list[OpenRouterModelRead], db: AsyncSession) -> None:
    changed = False
    provider_codes = sorted({model.provider for model in models if model.provider})
    for provider_code in provider_codes:
        result = await db.execute(select(ProviderConfig).where(ProviderConfig.provider_code == provider_code))
        if result.scalar_one_or_none() is None:
            db.add(
                ProviderConfig(
                    provider_code=provider_code,
                    display_name=provider_code,
                    is_allowlisted=True,
                    supports_zdr=False,
                    is_trusted_for_sensitive=False,
                    is_enabled=True,
                )
            )
            changed = True
    if changed:
        await db.commit()


async def _ensure_model_provider_config(model_name: str, provider_code: str, db: AsyncSession) -> None:
    provider = await db.execute(select(ProviderConfig).where(ProviderConfig.provider_code == provider_code))
    if provider.scalar_one_or_none() is not None:
        return

    model = await openrouter_model_service.find_model(model_name, provider_code)
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OpenRouter model/provider pair is unavailable")
    db.add(
        ProviderConfig(
            provider_code=provider_code,
            display_name=provider_code,
            is_allowlisted=True,
            supports_zdr=model.supports_zdr,
            is_trusted_for_sensitive=False,
            is_enabled=True,
        )
    )
    await db.commit()


async def _validate_openrouter_model_choice(model_name: str, provider_code: str) -> None:
    model = await openrouter_model_service.find_model(model_name, provider_code)
    if model is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OpenRouter model/provider pair is unavailable")
    if not model.is_available:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="OpenRouter model is unavailable")
