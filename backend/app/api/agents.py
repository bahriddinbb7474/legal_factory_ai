from fastapi import APIRouter, Depends
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent
from app.db.session import get_db
from app.schemas.agents import AgentRead


router = APIRouter(prefix="/api/agents", tags=["agents"])

DEFAULT_AGENTS = [
    {"code": "agent_1", "name": "Fast low-cost lawyer", "model_name": "", "is_enabled": True},
    {"code": "agent_2", "name": "Strong legal analyst", "model_name": "", "is_enabled": True},
    {"code": "agent_3", "name": "Reviewer / critic", "model_name": "", "is_enabled": True},
]


async def ensure_default_agents(db: AsyncSession) -> None:
    result = await db.execute(select(Agent.id).limit(1))
    if result.scalar_one_or_none() is not None:
        return

    db.add_all(Agent(**agent) for agent in DEFAULT_AGENTS)
    await db.commit()


@router.get("", response_model=list[AgentRead])
async def list_agents(db: AsyncSession = Depends(get_db)) -> list[Agent]:
    await ensure_default_agents(db)
    result = await db.execute(select(Agent).order_by(Agent.id))
    return list(result.scalars().all())
