import uuid

import uuid6

from backend.src.v1.filesystem.domain.interfaces import IFileRepo
from sqlalchemy.ext.asyncio import AsyncSession

class PgFileRepo(IFileRepo):
    def __init__(self, session: AsyncSession):
        super().__init__()
        self.session = session

    async def get_file_by_id(self, id: uuid.UUID):
        pass

    async def get_file_by_name(self, name: str):
        pass

    async def get_files(self):
        pass

    async def create_file(self, name: str, content_type: str, s3_key: uuid6.UUID):
        pass

    async def update_file(self, id: uuid.UUID):
        pass

    async def delete_file(self, id: uuid.UUID):
        pass