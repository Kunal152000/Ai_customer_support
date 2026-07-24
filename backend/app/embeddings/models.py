from uuid import UUID, uuid4
import os
from pgvector.sqlalchemy import Vector
from sqlalchemy import ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base


class DocumentEmbedding(Base):

    __tablename__ = "document_embeddings"

    id: Mapped[UUID] = mapped_column(primary_key=True,default=uuid4)

    chunk_id: Mapped[UUID] = mapped_column(ForeignKey("documents_chunks.id",ondelete="CASCADE"))

    embedding = mapped_column(
        Vector(int(os.getenv("EMBEDDING_DIMENSION"))))

    model: Mapped[str]
    # instead of calling db two times one to get chunk_id from the embedding and then get the actual chunk , we use relationship to get the direct relation between both chunk table and embedding table
    chunk = relationship("DocumentChunk",back_populates="embedding")