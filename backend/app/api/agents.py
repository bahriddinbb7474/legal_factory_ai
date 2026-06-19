from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent
from app.db.session import get_db
from app.schemas.agents import AgentRead
from app.services.agent_seed import ensure_default_config
from app.services.current_user import get_current_user


router = APIRouter(prefix="/api/agents", tags=["agents"], dependencies=[Depends(get_current_user)])

@router.get("", response_model=list[AgentRead])
async def list_agents(db: AsyncSession = Depends(get_db)) -> list[Agent]:
    await ensure_default_config(db)
    result = await db.execute(select(Agent).order_by(Agent.id))
    return list(result.scalars().all())
