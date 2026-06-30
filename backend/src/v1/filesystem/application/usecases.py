from dataclasses import dataclass
import uuid

import uuid6

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases
from backend.config.config import settings
from backend.src.v1.filesystem.presentation.dtos import UploadLinkRequest, UploadLinkResponse

@dataclass
class FsUsecases(IFsUsecases):
    uow: IUnitOfWork
    aws_service: IAwsService
    file_repo: IFileRepo

    async def upload_file(self, body: UploadLinkRequest) -> UploadLinkResponse:
        file_id = str(uuid6.uuid7())
        extension = body.filename.split(".")[-1] if "." in body.filename else ""
        s3_object_key = f"{file_id}.{extension}" if extension else file_id
        content_type = body.content_type
        
        upload_url = await self.aws_service.generate_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.minio.FILE_BUCKET_NAME,
                "Key": s3_object_key,
                "ContentType": content_type,
            },
            ExpiresIn=3600
        )
        
        async with self.uow as uow:
            result = await uow.file_repo.create_file(name = body.filename, content_type = content_type, s3_key = s3_object_key)

        return UploadLinkResponse(file_id=file_id, upload_url=upload_url)    

    async def get_file(self, id: uuid.UUID):
        result = await self.file_repo.get_by_id(id = id)
        return result

    async def get_files(self):
        result = await self.file_repo.get_files()
        return result

