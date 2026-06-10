from datetime import datetime
from typing import Optional

from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, JSON, Numeric, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )


class Role(Base, TimestampMixin):
    __tablename__ = "roles"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    name: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    description: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)

    users: Mapped[list["User"]] = relationship(back_populates="role")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role_id: Mapped[Optional[int]] = mapped_column(ForeignKey("roles.id"), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    role: Mapped[Optional["Role"]] = relationship(back_populates="users")
    chats: Mapped[list["Chat"]] = relationship(back_populates="owner")


class Agent(Base, TimestampMixin):
    __tablename__ = "agents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(32), unique=True, index=True, nullable=False)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)

    messages: Mapped[list["Message"]] = relationship(back_populates="agent")
    cost_records: Mapped[list["CostRecord"]] = relationship(back_populates="agent")


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)

    owner: Mapped[Optional["User"]] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="chat")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="chat")
    cost_records: Mapped[list["CostRecord"]] = relationship(back_populates="chat")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agents.id"), nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="messages")


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chats.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)

    chat: Mapped[Optional["Chat"]] = relationship(back_populates="documents")


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="approvals")


class CostRecord(Base, TimestampMixin):
    __tablename__ = "cost_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agents.id"), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)

    chat: Mapped["Chat"] = relationship(back_populates="cost_records")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="cost_records")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    action: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_type: Mapped[str] = mapped_column(String(128), nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    details: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
