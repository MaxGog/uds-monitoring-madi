import contextlib
import logging
import aioboto3
from minio import Minio 
from typing import AsyncContextManager

from types_aiobotocore_s3 import S3Client
from backend.config.config import settings
from urllib3.exceptions import MaxRetryError
from aiobotocore.session import get_session

logger = logging.getLogger(__name__)

async def check_aws_connection(s3_client) -> bool:
    try:
        result = await s3_client.list_buckets()
        logger.debug(result)
        logger.info("Successfully connected to S3 Client.")
        return True
    except Exception as e:
        logger.error(f"S3 connection health check failed: {e}")
        return False
    
class MinioClientFactory:
    def __init__(self):
        self.endpoint = settings.minio.MINIO_ENDPOINT
        self.access_key = settings.minio.MINIO_ADMIN
        self.secret_key = settings.minio.MINIO_PASS
        self.use_ssl = settings.minio.MINIO_SSL
        self.session = get_session()

    @contextlib.asynccontextmanager
    async def get_minio_client(self) -> S3Client:
        async with self.session.create_client(
            "s3",
            endpoint_url=self.endpoint,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            use_ssl= self.use_ssl
        ) as client:
            yield client

