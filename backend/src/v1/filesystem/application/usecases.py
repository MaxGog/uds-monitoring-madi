from dataclasses import dataclass
from datetime import timedelta
import uuid

from fastapi import HTTPException, status
import uuid6

from backend.core.db.postgres.data_orms.user_orm import Document, FileAccessType, RoleName
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases
from backend.config.config import settings
from backend.src.v1.filesystem.presentation.dtos import UploadLinkRequest, UploadLinkResponse

@dataclass
class FsUsecases(IFsUsecases):
    uow: IUnitOfWork
    aws_service: IAwsService
    file_repo: IFileRepo
    user_repo: IUserRepo

    async def generate_upload_url(self, user_id: str, body: UploadLinkRequest) -> UploadLinkResponse:
        role = await self.user_repo.get_role(user_id)
    
        if role == RoleName.VIEWER:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
        if role != RoleName.ADMIN:
            # Выполнить проверку прав доступа для кастомной роли по ACL
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
        
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

        # Для правильной синхронизации необходимо с помощью встроенных инструментов Minio (SQS)
        # или Webhooks и сообщать о загрузке файла Postgresql и передавать ему UUID файла.
        async with self.uow as uow:
            await uow.file_repo.create_file(file_id = file_id, user_id = user_id, name = body.filename, content_type = content_type, s3_key = s3_object_key)

        return UploadLinkResponse(file_id=file_id, upload_url=upload_url)  

    async def get_file(self, user_id: uuid.UUID, file_id: uuid.UUID):
        role = await self.user_repo.get_role(user_id)
    
        if role not in (RoleName.ADMIN, RoleName.VIEWER):
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN)
            # Для других ролей проверка прав доступа ACL по файлам        
            # file_meta = await self.uow.files.get_by_id(file_id)
            # if not file_meta:
            #     raise NotFoundException("Файл не найден")

            # # Проверка А: Является ли пользователь создателем/владельцем файла
            # if file_meta.owner_id == user_id:
            #     return await self.aws_service.generate_url(file_id)

            # # Проверка Б: Проверяем таблицу кастомных прав (ACL / ReBAC)
            # # Ищем запись, где разрешено действие 'read' для этого user_id и file_id
            # has_acl_access = await self.uow.permissions.check_file_access(
            #     user_id=user_id,
            #     file_id=file_id,
            #     action="read"
            # )
            
            # if has_acl_access:
            #     return await self.aws_service.generate_url(file_id)

        download_url = await self.aws_service.generate_url(
            ClientMethod='get_object',
            Params = {
                'Bucket': settings.minio.FILE_BUCKET_NAME,
                'Key': f"files/{file_id}",
                #'ResponseContentDisposition': content_disposition
            },
            ExpiresIn=3600,
        )
        result = await self.file_repo.get_by_id(id = file_id)
        return (result, download_url)

    async def get_files(
            self,
            user_id: uuid.UUID,
            required_action: FileAccessType,
            limit: int = 100,
            offset: int = 0,
            ) -> list[Document]:
        role = await self.user_repo.get_role(user_id)

        if role in (RoleName.ADMIN, RoleName.VIEWER):
            result = await self.file_repo.get_files()
            return result

        # Для кастомной роли будут проверяться полноценно права доступа, драфтовый код:

        # has_acl_permission = exists().where(
        #     FilePermission.file_id == File.id,
        #     FilePermission.user_id == user_id
        # )

        # stmt = stmt.where(
        #     or_(
        #         File.owner_id == user_id,
        #         has_acl_permission
        #     )
        # )

        # stmt = stmt.order_by(File.id.desc()).limit(limit).offset(offset)

        # result = await db.execute(stmt)
        # return list(result.scalars().all())

        return []

