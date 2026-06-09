from app.core.database import Base
from sqlalchemy import Column, String, Integer, DateTime, Enum
from datetime import datetime
import enum

class DocumentStatus(str, enum.Enum):
    UPLOADED = "uploaded"
    PARSING = "parsing"
    INDEXING = "indexing"
    INDEXED = "indexed"
    FAILED = "failed"

class Document(Base):
    __tablename__ = "documents"

    id            = Column(String(36), primary_key=True)    # uuid dạng string
    original_name = Column(String(255), nullable=False)
    file_path     = Column(String(500), nullable=False)
    file_type     = Column(String(10), nullable=False)
    file_size     = Column(Integer, nullable=False)
    status        = Column(Enum(DocumentStatus), default=DocumentStatus.UPLOADED)
    chunk_count   = Column(Integer, default=0)
    uploaded_at   = Column(DateTime, default=datetime.utcnow)
    indexed_at    = Column(DateTime, nullable=True)