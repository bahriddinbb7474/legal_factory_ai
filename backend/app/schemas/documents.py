from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentBase(BaseModel):
    original_filename: str
    storage_key: str
    mime_type: str
    file_size: int
    file_hash: str
    category: str
    suggested_category: str
    counterparty: str | None = None
    document_number: str | None = None
    document_date: str | None = None
    sensitivity: str
    uploaded_by_user_id: int | None = None
    extraction_status: str
    extracted_text_storage_key: str | None = None
    ocr_status: str
    status: str = "draft"


class DocumentRead(DocumentBase):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class DocumentContentRead(BaseModel):
    document: DocumentRead
    extracted_text: str


class ChatDocumentRead(BaseModel):
    chat_id: int
    document: DocumentRead
    created_at: datetime


class DocumentUploadResponse(BaseModel):
    document: DocumentRead
    extraction_error: str | None = None
