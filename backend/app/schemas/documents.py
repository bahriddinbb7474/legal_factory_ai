from datetime import datetime

from pydantic import BaseModel, ConfigDict


class DocumentCreate(BaseModel):
    chat_id: int | None = None
    filename: str
    file_type: str
    storage_path: str
    status: str = "draft"


class DocumentRead(DocumentCreate):
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
