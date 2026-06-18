from datetime import datetime

from pydantic import BaseModel, ConfigDict


class GenerateDocumentFromVerdictRequest(BaseModel):
    agent_code: str
    document_type: str
    title: str
    template_key: str | None = None


class GeneratedDocumentUpdate(BaseModel):
    title: str | None = None
    content: str | None = None
    status: str | None = None


class GeneratedDocumentRead(BaseModel):
    id: int
    chat_id: int
    verdict_message_id: int
    created_by_agent_id: int | None = None
    title: str
    document_type: str
    template_key: str | None = None
    content: str
    status: str
    storage_key: str | None = None
    docx_storage_key: str | None = None
    pdf_storage_key: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class SendGeneratedDocumentToChatResponse(BaseModel):
    message_id: int
    document_id: int
