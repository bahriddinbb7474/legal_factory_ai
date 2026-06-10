from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.base import Chat, CostRecord, Message
from app.db.session import get_db
from app.schemas.chats import ChatCreate, ChatRead
from app.schemas.costs import CostRecordRead
from app.schemas.messages import MessageCreate, MessageRead


router = APIRouter(prefix="/api/chats", tags=["chats"])


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
