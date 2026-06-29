from minio import Minio
from uuid6 import uuid7
from backend.config.config import settings
from backend.src.v1.filesystem.domain.interfaces import IAwsService

class MinioFileService(IAwsService):
    def __init__(self, client: Minio):
        self.client = client
        self.bucket_name = settings.minio.FILE_BUCKET_NAME
    
    def upload_file(self, file_data, content_type: str) -> str:
        s3_key = f"{uuid7}"
        self.client.put_object(
            bucket_name = self.bucket_name,
            object_name = s3_key,
            data = file_data,
            length = 1,
            part_size = 10 * 1024 * 1024,
            content_type = content_type
        )
        return s3_key