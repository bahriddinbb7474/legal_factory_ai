from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import delete, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent, AuditLog, AuthSession, ProviderConfig, User
from app.db.session import get_db
from app.schemas.agents import AgentRead, AgentUpdate
from app.schemas.audit import AuditLogRead
from app.schemas.openrouter import OpenRouterModelRead
from app.schemas.providers import ProviderRead, ProviderUpdate
from app.schemas.users import UserCreate, UserPasswordReset, UserRead, UserRole, UserUpdate
from app.services.agent_seed import LAWYER_PROVIDER_ERROR, ensure_default_config, validate_distinct_lawyer_providers
from app.services.audit import write_audit_log
from app.services.auth import hash_password
from app.services.current_user import CurrentUser, get_current_user, require_role
from app.services.openrouter_models import openrouter_model_service


router = APIRouter(prefix="/api/admin", tags=["admin"], dependencies=[Depends(require_role("admin"))])


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


@router.get("/audit-logs", response_model=list[AuditLogRead])
async def list_audit_logs(
    action: str | None = None,
    entity_type: str | None = None,
    limit: int = Query(default=100, ge=1, le=500),
    offset: int = Query(default=0, ge=0),
    db: AsyncSession = Depends(get_db),
) -> list[AuditLog]:
    query = select(AuditLog).order_by(AuditLog.created_at.desc(), AuditLog.id.desc())
    if action is not None:
        query = query.where(AuditLog.action == action)
    if entity_type is not None:
        query = query.where(AuditLog.entity_type == entity_type)
    query = query.limit(limit).offset(offset)
    result = await db.execute(query)
    return list(result.scalars().all())


@router.post("/openrouter/models/refresh", response_model=list[OpenRouterModelRead])
async def refresh_openrouter_models(db: AsyncSession = Depends(get_db)) -> list[OpenRouterModelRead]:
    try:
        models = await openrouter_model_service.list_models(refresh=True)
    except Exception as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="OpenRouter model list unavailable") from exc
    await _ensure_model_providers(models, db)
    return models


@router.get("/users", response_model=list[UserRead])
async def list_admin_users(db: AsyncSession = Depends(get_db)) -> list[User]:
    result = await db.execute(select(User).order_by(User.id))
    return list(result.scalars().all())


@router.post("/users", response_model=UserRead, status_code=status.HTTP_201_CREATED)
async def create_admin_user(
    payload: UserCreate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    email = payload.email.strip().lower()
    existing = await db.scalar(select(User).where(User.email == email))
    if existing is not None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=email,
        full_name=payload.full_name.strip(),
        role=payload.role.value,
        password_hash=hash_password(payload.password),
        is_active=payload.is_active,
    )
    db.add(user)
    await db.flush()
    await write_audit_log(
        db,
        action="user.created",
        entity_type="user",
        entity_id=user.id,
        user_id=current_user.id,
        details={"email": user.email, "role": user.role},
    )
    await db.commit()
    await db.refresh(user)
    return user


@router.patch("/users/{user_id}", response_model=UserRead)
async def update_admin_user(
    user_id: int,
    payload: UserUpdate,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_or_404(user_id, db)
    update_data = payload.model_dump(exclude_unset=True)

    if user.role == UserRole.admin.value:
        will_deactivate = "is_active" in update_data and not update_data["is_active"]
        will_demote = "role" in update_data and update_data["role"] != UserRole.admin
        if will_deactivate or will_demote:
            await _check_last_active_admin(user_id, db)

    old_role = user.role
    old_is_active = user.is_active

    for field, value in update_data.items():
        setattr(user, field, value.value if isinstance(value, UserRole) else value)

    _SAFE_AUDIT_FIELDS = {"full_name", "role", "is_active"}
    changed_fields = [f for f in update_data if f in _SAFE_AUDIT_FIELDS]
    changes: dict = {}
    if "role" in update_data:
        changes["role"] = {"from": old_role, "to": user.role}
    if "is_active" in update_data:
        changes["is_active"] = {"from": old_is_active, "to": user.is_active}
    if "full_name" in update_data:
        changes["full_name_changed"] = True

    await write_audit_log(
        db,
        action="user.updated",
        entity_type="user",
        entity_id=user_id,
        user_id=current_user.id,
        details={"changed_fields": changed_fields, "changes": changes},
    )

    deactivating = old_is_active and "is_active" in update_data and not update_data["is_active"]
    if deactivating:
        await write_audit_log(
            db,
            action="user.deactivated",
            entity_type="user",
            entity_id=user_id,
            user_id=current_user.id,
        )

    await db.commit()

    if "is_active" in update_data and not update_data["is_active"]:
        await db.execute(delete(AuthSession).where(AuthSession.user_id == user_id))
        await db.commit()

    await db.refresh(user)
    return user


@router.post("/users/{user_id}/reset-password", response_model=UserRead)
async def reset_admin_user_password(
    user_id: int,
    payload: UserPasswordReset,
    current_user: CurrentUser = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
) -> User:
    user = await _get_user_or_404(user_id, db)
    user.password_hash = hash_password(payload.new_password)
    await write_audit_log(
        db,
        action="user.password_reset",
        entity_type="user",
        entity_id=user_id,
        user_id=current_user.id,
    )
    await db.commit()
    await db.execute(delete(AuthSession).where(AuthSession.user_id == user_id))
    await db.commit()
    await db.refresh(user)
    return user


async def _get_user_or_404(user_id: int, db: AsyncSession) -> User:
    user = await db.get(User, user_id)
    if user is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    return user


async def _check_last_active_admin(excluded_user_id: int, db: AsyncSession) -> None:
    count = await db.scalar(
        select(func.count(User.id)).where(
            User.role == UserRole.admin.value,
            User.is_active.is_(True),
            User.id != excluded_user_id,
        )
    )
    if count == 0:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Cannot deactivate or demote the last active admin")


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
