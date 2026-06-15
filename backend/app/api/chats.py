from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Agent, Chat, CostRecord, Message, ProviderConfig
from app.db.session import get_db
from app.schemas.chats import ChatCreate, ChatRead
from app.schemas.costs import CostRecordRead
from app.schemas.messages import MessageCreate, MessageRead
from app.schemas.openrouter import InvokeAgentRequest
from app.services.agent_seed import LAWYER_PROVIDER_ERROR, ensure_default_config, validate_distinct_lawyer_providers
from app.services.chat_context import author_type_for_agent, build_chat_context
from app.services.costs import calculate_cost_usd
from app.services.llm_gateway import LLMGatewayError, MissingOpenRouterKeyError, OpenRouterGateway, openrouter_gateway


router = APIRouter(prefix="/api/chats", tags=["chats"])


def get_llm_gateway() -> OpenRouterGateway:
    return openrouter_gateway


@router.get("", response_model=list[ChatRead])
async def list_chats(db: AsyncSession = Depends(get_db)) -> list[Chat]:
    result = await db.execute(select(Chat).order_by(Chat.created_at.desc(), Chat.id.desc()))
    return list(result.scalars().all())


@router.post("", response_model=ChatRead, status_code=status.HTTP_201_CREATED)
async def create_chat(payload: ChatCreate, db: AsyncSession = Depends(get_db)) -> Chat:
    chat = Chat(**payload.model_dump())
    db.add(chat)
    await db.commit()
    await db.refresh(chat)
    return chat


@router.get("/{chat_id}", response_model=ChatRead)
async def get_chat(chat_id: int, db: AsyncSession = Depends(get_db)) -> Chat:
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


@router.get("/{chat_id}/messages", response_model=list[MessageRead])
async def list_messages(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[Message]:
    await _get_chat_or_404(chat_id, db)
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at, Message.id)
    )
    return list(result.scalars().all())


@router.post("/{chat_id}/messages", response_model=MessageRead, status_code=status.HTTP_201_CREATED)
async def create_message(
    chat_id: int,
    payload: MessageCreate,
    db: AsyncSession = Depends(get_db),
) -> Message:
    await _get_chat_or_404(chat_id, db)
    message = Message(chat_id=chat_id, **payload.model_dump())
    db.add(message)
    await db.commit()
    await db.refresh(message)
    return message


@router.post("/{chat_id}/invoke", response_model=MessageRead)
async def invoke_agent(
    chat_id: int,
    payload: InvokeAgentRequest,
    db: AsyncSession = Depends(get_db),
    gateway: OpenRouterGateway = Depends(get_llm_gateway),
) -> Message:
    await ensure_default_config(db)
    await _get_chat_or_404(chat_id, db)

    agent = await _get_agent_or_404(payload.agent_code, db)
    if not agent.is_enabled:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Selected lawyer is disabled")

    try:
        await validate_distinct_lawyer_providers(db)
    except ValueError as exc:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=LAWYER_PROVIDER_ERROR) from exc

    provider = await _get_provider_or_404(agent.provider_code, db)
    if not provider.is_enabled or not provider.is_allowlisted:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Provider is not allowlisted")

    messages = await _list_chat_messages(chat_id, db)
    if not any(message.author_type == "user" for message in messages):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="No user message found in chat")

    chat_context = build_chat_context(messages)
    try:
        llm_response = await gateway.invoke(agent, chat_context)
    except MissingOpenRouterKeyError as exc:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=str(exc)) from exc
    except LLMGatewayError as exc:
        raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail=str(exc)) from exc

    cost_usd = calculate_cost_usd(
        llm_response.input_tokens,
        llm_response.output_tokens,
        Decimal(agent.input_price_per_1m),
        Decimal(agent.output_price_per_1m),
    )
    message = Message(
        chat_id=chat_id,
        role="assistant",
        author_type=author_type_for_agent(agent.code),
        content=llm_response.content,
        agent_id=agent.id,
        model_id=llm_response.model_id,
        provider_code=llm_response.provider_code,
        input_tokens=llm_response.input_tokens,
        output_tokens=llm_response.output_tokens,
        cost_usd=cost_usd,
    )
    db.add(message)
    db.add(
        CostRecord(
            chat_id=chat_id,
            agent_id=agent.id,
            provider_code=llm_response.provider_code,
            model_id=llm_response.model_id,
            input_tokens=llm_response.input_tokens,
            output_tokens=llm_response.output_tokens,
            cost_usd=cost_usd,
        )
    )
    await db.commit()
    await db.refresh(message)
    return message


@router.get("/{chat_id}/costs", response_model=list[CostRecordRead])
async def list_costs(chat_id: int, db: AsyncSession = Depends(get_db)) -> list[CostRecord]:
    await _get_chat_or_404(chat_id, db)
    result = await db.execute(
        select(CostRecord).where(CostRecord.chat_id == chat_id).order_by(CostRecord.created_at, CostRecord.id)
    )
    return list(result.scalars().all())


async def _get_chat_or_404(chat_id: int, db: AsyncSession) -> Chat:
    chat = await db.get(Chat, chat_id)
    if chat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Chat not found")
    return chat


async def _list_chat_messages(chat_id: int, db: AsyncSession) -> list[Message]:
    result = await db.execute(
        select(Message).where(Message.chat_id == chat_id).order_by(Message.created_at, Message.id)
    )
    return list(result.scalars().all())


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
