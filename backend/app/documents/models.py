from uuid import uuid4
from datetime import datetime
from sqlalchemy import (
    DateTime,
    String,
    BigInteger,
    Integer,
    func,
    Enum
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import Mapped, mapped_column
from app.documents.enums import DocumentStatus, DocumentType
from app.database.base import Base



class DocumentMetadata(Base):

    __tablename__ = "documents_metadata"

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid4,
    )

    # Ownership
    owner_name: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    # Original file details
    original_filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    stored_filename: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    storage_location: Mapped[str] = mapped_column(
        String(500),
        nullable=False,
    )

    # File metadata
    document_type: Mapped[DocumentType] = mapped_column(
        Enum(DocumentType,name="document_type_enum"),
        nullable=False,
    )

    # mime_type: Mapped[str] = mapped_column(
    #     String(100),
    #     nullable=False,
    # )

    file_size: Mapped[int] = mapped_column(
        BigInteger,
        nullable=False,
    )

    # file_hash: Mapped[str] = mapped_column(
    #     String(64),
    #     nullable=False,
    # )

    # Lifecycle
    status: Mapped[DocumentStatus] = mapped_column(
        Enum(DocumentStatus,name="document_status_enum"),
        default=DocumentStatus.UPLOADED,
        nullable=False,
    )

    version: Mapped[int] = mapped_column(
        Integer,
        default=1,
        nullable=False,
    )

    # Optional metadata (can be populated later)
    # language: Mapped[str | None] = mapped_column(
    #     String(20),
    #     nullable=True,
    # )

    # page_count: Mapped[int | None] = mapped_column(
    #     nullable=True,
    # )

    # author: Mapped[str | None] = mapped_column(
    #     String(255),
    #     nullable=True,
    # )

    title: Mapped[str | None] = mapped_column(
        String(255),
        nullable=True,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
    )