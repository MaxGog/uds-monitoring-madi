from typing import List, Optional
import uuid

from sqlalchemy import insert, select
import uuid6

from backend.core.db.postgres.data_orms.document_orm import Document
from backend.src.v1.filesystem.domain.interfaces import IFileRepo
from backend.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

class PgFileRepo(IFileRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, item_id: uuid.UUID) -> Optional[Document]:
        return await self.session.get(Document, item_id)

    async def get_all(self, owner_type: Optional[str] = None, owner_id: Optional[int] = None) -> List[Document]:
        stmt = select(Document)
        
        # Динамическая фильтрация по владельцу файла
        if owner_type:
            stmt = stmt.where(Document.owner_type == owner_type)
        if owner_id:
            stmt = stmt.where(Document.owner_id == owner_id)
            
        stmt = stmt.order_by(Document.created_at.desc())
        result = await self.session.execute(stmt)
        return list(result.scalars().all())

    async def add(self, document: Document) -> None:
        self.session.add(document)

    async def delete(self, document: Document) -> None:
        await self.session.delete(document)