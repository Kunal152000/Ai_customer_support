from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.documents.models import DocumentMetadata


class DocumentRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_document( self, document: DocumentMetadata) -> DocumentMetadata: 
        self.db.add(document)
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def get_document(self,document_id: UUID,) -> DocumentMetadata | None:
        result = await self.db.execute(
            select(DocumentMetadata).where(
                DocumentMetadata.id == document_id
            )
        )
        return result.scalar_one_or_none()

    async def update_document(self,document: DocumentMetadata,) -> DocumentMetadata:
        await self.db.commit()
        await self.db.refresh(document)
        return document

    async def delete_document(self, document: DocumentMetadata,) -> None:
        await self.db.delete(document)
        await self.db.commit()
        
    async def list_documents( self, ) -> list[DocumentMetadata]:
        result = await self.db.execute(
            select(DocumentMetadata).order_by(
                DocumentMetadata.created_at.desc()
            )
        )
        return list(result.scalars().all())