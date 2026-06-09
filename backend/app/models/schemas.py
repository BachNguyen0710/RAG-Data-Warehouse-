
from pydantic import BaseModel
from datetime import datetime
from typing import Optional
from app.models.db_models import DocumentStatus

class DocumentOut(BaseModel):
    id:            str
    original_name: str
    file_type:     str
    file_size:     int
    status:        DocumentStatus
    chunk_count:   int
    uploaded_at:   datetime
    indexed_at:    Optional[datetime] = None

    model_config = {"from_attributes": True}  # pydantic v2


class ChatRequest(BaseModel):
    question:    str
    top_k:       int = 5
    temperature: float = 0.2


class ChatResponse(BaseModel):
    answer:   str
    sources:  list[str]
    duration: float