import logging
import os
import tempfile
from uuid import UUID

import aiofiles
from types_aiobotocore_s3 import S3Client
from backend.config.config import settings
from backend.src.v1.filesystem.domain.interfaces import IAwsService

logger = logging.getLogger(__file__)

class MinioFileService(IAwsService):
    def __init__(self, client: S3Client):
        self.client = client
    
    async def generate_url(self, ClientMethod: str, Params: dict, ExpiresIn: int):
        presigned_url = await self.client.generate_presigned_url(
            ClientMethod=ClientMethod,
            Params=Params,
            ExpiresIn=ExpiresIn
        )
        return presigned_url
    
    async def generate_upload_url(self, s3_key: str, content_type: str, uploader_id: UUID, owner_type: str | None, owner_id: int | None) -> str | None:
        """
        Генерирует ссылку, заставляя MinIO ожидать метаданные файла.
        """
        try:
            metadata = {"uploader-id": str(uploader_id)}
            
            if owner_type:
                metadata["owner-type"] = owner_type if hasattr(owner_type, 'value') else str(owner_type)
                
            if owner_id is not None:
                metadata["owner-id"] = str(owner_id)
                
            return await self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": settings.minio.FILE_BUCKET_NAME,
                    "Key": s3_key,
                    "ContentType": content_type,
                    "Metadata": metadata
                },
                ExpiresIn=15 * 60,
                HttpMethod="PUT"
            )
        except Exception as e:
            logger.error(e)

    async def generate_download_url(self, bucket: str, s3_key: str, expires_minutes: int = 60) -> str:
        """
        Генерирует временную ссылку для скачивания или просмотра файла (GET).
        """
        return await self.client.generate_presigned_url(
            ClientMethod="get_object",
            Params={
                "Bucket": bucket,
                "Key": s3_key,
            },
            ExpiresIn=expires_minutes * 60
        )

    async def get_object_stats(self, bucket: str, s3_key: str):
        """
        В S3-совместимых хранилищах аналог stat_object — это head_object.
        Возвращает словарь с ContentLength, ContentType, ETag и т.д.
        """
        return await self.client.head_object(Bucket=bucket, Key=s3_key)

    async def delete_object(self, bucket: str, s3_key: str) -> None:
        await self.client.delete_object(Bucket=bucket, Key=s3_key)


    # Для celery
    async def upload_file(self, file_obj, s3_key: str, content_type: str, metadata: dict):
        file_bytes = file_obj.read()
        await self.client.put_object(
            Bucket=settings.minio.FILE_BUCKET_NAME,
            Key=s3_key,
            Body=file_bytes,
            ContentType=content_type,
            Metadata=metadata
        )
    # Для celery
    async def download_file(self, s3_key: str) -> str:
        """Скачивает файл во временный локальный файл и возвращает путь к нему"""
        # Celery воркер скачает файл локально, чтобы openpyxl мог его прочитать
        temp_dir = tempfile.gettempdir()
        local_path = os.path.join(temp_dir, os.path.basename(s3_key))
        response = await self.client.get_object(
            Bucket=settings.minio.FILE_BUCKET_NAME,
            Key=s3_key,
        )

        async with aiofiles.open(local_path, "wb") as f:
            async for chunk in response["Body"].iter_chunks():
                await f.write(chunk)
        return local_path