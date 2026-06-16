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
    display_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    provider_code: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    system_prompt: Mapped[str] = mapped_column(Text, default="", nullable=False)
    role_type: Mapped[str] = mapped_column(String(64), default="", nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    input_price_per_1m: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    output_price_per_1m: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    supports_zdr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)

    messages: Mapped[list["Message"]] = relationship(back_populates="agent")
    cost_records: Mapped[list["CostRecord"]] = relationship(back_populates="agent")


class Chat(Base, TimestampMixin):
    __tablename__ = "chats"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    owner_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    approval_status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)

    owner: Mapped[Optional["User"]] = relationship(back_populates="chats")
    messages: Mapped[list["Message"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    documents: Mapped[list["Document"]] = relationship(back_populates="chat")
    chat_documents: Mapped[list["ChatDocument"]] = relationship(back_populates="chat", cascade="all, delete-orphan")
    approvals: Mapped[list["Approval"]] = relationship(back_populates="chat")
    cost_records: Mapped[list["CostRecord"]] = relationship(back_populates="chat")


class Message(Base, TimestampMixin):
    __tablename__ = "messages"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    role: Mapped[str] = mapped_column(String(32), nullable=False)
    author_type: Mapped[str] = mapped_column(String(32), nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agents.id"), nullable=True)
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    provider_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    input_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    output_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    cost_usd: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    structured_payload: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    raw_response: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    risk: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    confidence: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    approval_required: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    source_check_status: Mapped[str] = mapped_column(String(32), default="not_checked", nullable=False)
    red_flag_codes: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)

    chat: Mapped["Chat"] = relationship(back_populates="messages")
    agent: Mapped[Optional["Agent"]] = relationship(back_populates="messages")
    message_documents: Mapped[list["MessageDocument"]] = relationship(back_populates="message", cascade="all, delete-orphan")


class ProviderConfig(Base, TimestampMixin):
    __tablename__ = "provider_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    provider_code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    is_allowlisted: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    supports_zdr: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_trusted_for_sensitive: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class ModelConfig(Base, TimestampMixin):
    __tablename__ = "model_configs"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    agent_code: Mapped[str] = mapped_column(String(32), index=True, nullable=False)
    provider_code: Mapped[str] = mapped_column(String(64), index=True, nullable=False)
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    input_price_per_1m: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    output_price_per_1m: Mapped[float] = mapped_column(Numeric(12, 6), default=0, nullable=False)
    max_context_tokens: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    supports_structured_output: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    supports_vision: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)


class Document(Base, TimestampMixin):
    __tablename__ = "documents"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[Optional[int]] = mapped_column(ForeignKey("chats.id"), nullable=True)
    filename: Mapped[str] = mapped_column(String(255), nullable=False)
    file_type: Mapped[str] = mapped_column(String(64), nullable=False)
    storage_path: Mapped[str] = mapped_column(String(500), nullable=False)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    original_filename: Mapped[str] = mapped_column(String(255), default="", nullable=False)
    storage_key: Mapped[str] = mapped_column(String(500), default="", nullable=False)
    mime_type: Mapped[str] = mapped_column(String(128), default="", nullable=False)
    file_size: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    file_hash: Mapped[str] = mapped_column(String(64), default="", index=True, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="other", index=True, nullable=False)
    suggested_category: Mapped[str] = mapped_column(String(64), default="other", nullable=False)
    counterparty: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
    document_number: Mapped[Optional[str]] = mapped_column(String(128), nullable=True)
    document_date: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    sensitivity: Mapped[str] = mapped_column(String(32), default="normal", index=True, nullable=False)
    uploaded_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    extraction_status: Mapped[str] = mapped_column(String(32), default="pending", nullable=False)
    extracted_text_storage_key: Mapped[Optional[str]] = mapped_column(String(500), nullable=True)
    ocr_status: Mapped[str] = mapped_column(String(32), default="not_required", nullable=False)

    chat: Mapped[Optional["Chat"]] = relationship(back_populates="documents")
    chat_documents: Mapped[list["ChatDocument"]] = relationship(back_populates="document", cascade="all, delete-orphan")
    message_documents: Mapped[list["MessageDocument"]] = relationship(back_populates="document", cascade="all, delete-orphan")


class ChatDocument(Base):
    __tablename__ = "chat_documents"

    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), primary_key=True)
    added_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    chat: Mapped["Chat"] = relationship(back_populates="chat_documents")
    document: Mapped["Document"] = relationship(back_populates="chat_documents")


class MessageDocument(Base):
    __tablename__ = "message_documents"

    message_id: Mapped[int] = mapped_column(ForeignKey("messages.id"), primary_key=True)
    document_id: Mapped[int] = mapped_column(ForeignKey("documents.id"), primary_key=True)
    usage_type: Mapped[str] = mapped_column(String(32), default="attached", primary_key=True)
    created_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)

    message: Mapped["Message"] = relationship(back_populates="message_documents")
    document: Mapped["Document"] = relationship(back_populates="message_documents")


class Approval(Base, TimestampMixin):
    __tablename__ = "approvals"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    requested_by_user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), nullable=False)
    approved_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    status: Mapped[str] = mapped_column(String(32), default="draft", nullable=False)
    comment: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    entity_type: Mapped[str] = mapped_column(String(64), default="chat", nullable=False)
    entity_id: Mapped[Optional[int]] = mapped_column(Integer, nullable=True)
    action: Mapped[str] = mapped_column(String(64), default="request", nullable=False)
    performed_by_user_id: Mapped[Optional[int]] = mapped_column(ForeignKey("users.id"), nullable=True)
    performed_at: Mapped[datetime] = mapped_column(DateTime, default=datetime.utcnow, nullable=False)
    previous_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)
    new_status: Mapped[Optional[str]] = mapped_column(String(32), nullable=True)

    chat: Mapped["Chat"] = relationship(back_populates="approvals")


class CostRecord(Base, TimestampMixin):
    __tablename__ = "cost_records"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    chat_id: Mapped[int] = mapped_column(ForeignKey("chats.id"), nullable=False)
    agent_id: Mapped[Optional[int]] = mapped_column(ForeignKey("agents.id"), nullable=True)
    provider_code: Mapped[Optional[str]] = mapped_column(String(64), nullable=True)
    model_id: Mapped[Optional[str]] = mapped_column(String(255), nullable=True)
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


class RedFlagRule(Base, TimestampMixin):
    __tablename__ = "red_flag_rules"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True)
    code: Mapped[str] = mapped_column(String(64), unique=True, index=True, nullable=False)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    keywords: Mapped[list[str]] = mapped_column(JSON, default=list, nullable=False)
    category: Mapped[str] = mapped_column(String(64), default="general", nullable=False)
    amount_threshold: Mapped[Optional[float]] = mapped_column(Numeric(14, 2), nullable=True)
    is_enabled: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    required_approver: Mapped[str] = mapped_column(String(64), default="director", nullable=False)
