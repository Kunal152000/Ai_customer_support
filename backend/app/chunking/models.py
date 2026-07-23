from uuid import uuid4
from datetime import datetime
from sqlalchemy import (DateTime,String,Integer,func)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.database.base import Base

class DocumentChunk(Base):
    __tablename__ = "documents_chunks"

    id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),primary_key=True,default=uuid4)
    document_id: Mapped[UUID] = mapped_column(UUID(as_uuid=True),nullable=False)
    chunk_index: Mapped[int] = mapped_column(Integer,nullable=False)
    chunk_text: Mapped[str] = mapped_column(String,nullable=False)
    word_count: Mapped[int] = mapped_column(Integer,nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True),server_default=func.now(),nullable=False)
