import uuid

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.filesystem.domain.interfaces import IAwsService


class FsUsecases:
    uow: IUnitOfWork
    aws_service: IAwsService

    async def upload_file(self):
        pass

    async def generate_url(self):
        pass

    async def get_file(self, id: uuid.UUID):
        pass

    async def get_files(self):
        pass

