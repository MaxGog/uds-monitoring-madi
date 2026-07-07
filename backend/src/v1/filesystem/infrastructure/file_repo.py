import uuid

from sqlalchemy import insert, select
import uuid6

from backend.core.db.postgres.data_orms.user_orm import Document
from backend.src.v1.filesystem.domain.interfaces import IFileRepo
from backend.config.config import settings
from sqlalchemy.ext.asyncio import AsyncSession

from backend.src.v1.filesystem.presentation.dtos import FileCreateResponse

class PgFileRepo(IFileRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_by_id(self, id: uuid.UUID):
        stmt = select(Document).where(Document.id == id)
        result = await self.session.execute(stmt)
        return result.unique().scalar_one_or_none()
    
    async def get_by_name(self, name: str):
        pass

    async def get_files(self):
        stmt = select(Document)
        result = await self.session.execute(stmt)
        return result.unique().scalars().all()

    async def create_file(self, file_id: uuid.UUID, user_id, name: str, content_type: str, s3_key: uuid6.UUID) -> FileCreateResponse:
        document_orm = Document(
            id = file_id,
            owner_id = user_id,
            name = name,
            s3_bucket = settings.minio.FILE_BUCKET_NAME,
            s3_key = s3_key,
            content_type = content_type,
        )

        self.session.add(document_orm)

        await self.session.flush()

        result = FileCreateResponse(
            id = document_orm.id,
            s3_key = document_orm.s3_key,
            owner_id = document_orm.owner_id,
            name = document_orm.name,
            content_type = document_orm.content_type,
        )
        await self.session.commit()
        return result

    async def update_file(self, id: uuid.UUID):
        pass

    async def delete_file(self, id: uuid.UUID):
        pass