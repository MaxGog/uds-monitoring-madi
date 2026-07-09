from datetime import timedelta

from types_aiobotocore_s3 import S3Client
from uuid6 import uuid7
from backend.config.config import settings
from backend.src.v1.filesystem.domain.interfaces import IAwsService

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
    
    async def generate_upload_url(self, s3_key: str, content_type: str, uploader_id: str, owner_type: str, owner_id: int) -> str:
        """
        Генерирует ссылку, заставляя MinIO ожидать метаданные файла.
        """
        return await self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={
                "Bucket": settings.minio.FILE_BUCKET_NAME,
                "Key": s3_key,
                "ContentType": content_type,
                # Boto3 автоматически превратит ключи в заголовки x-amz-meta-*
                "Metadata": {
                    "uploader-id": str(uploader_id),
                    "owner-type": str(owner_type),
                    "owner-id": str(owner_id)
                }
            },
            ExpiresIn=15 * 60,
            HttpMethod="PUT"
        )
        
    # async def generate_upload_url(self, s3_key: str, content_type: str, expires_minutes: int = 15) -> str:
    #     """
    #     Генерирует presigned URL для загрузки файла методом PUT.
    #     Важно: при отправке файла клиент ОБЯЗАН передать точно такой же Content-Type в заголовках.
    #     """
    #     return await self.client.generate_presigned_url(
    #         ClientMethod="put_object",
    #         Params={
    #             "Bucket": settings.minio.FILE_BUCKET_NAME,
    #             "Key": s3_key,
    #             "ContentType": content_type,
    #         },
    #         ExpiresIn=expires_minutes * 60,  # Переводим минуты в секунды
    #         HttpMethod="PUT"
    #     )

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