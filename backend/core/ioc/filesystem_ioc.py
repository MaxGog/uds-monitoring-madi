from typing import AsyncIterator

import aioboto3
from botocore.exceptions import ClientError
from dishka import Provider, Scope, provide
from types_aiobotocore_s3 import S3Client
from backend.config.config import settings
from backend.core.db.aws.minio_conn import MinioClientFactory
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.application.file_permissions_usecases import FileAuthUsecases
from backend.src.v1.filesystem.application.usecases import FsUsecases
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileAuthUsecases, IFileRepo, IFsUsecases
from backend.src.v1.filesystem.infrastructure.aws_repo import MinioFileService

class FilesystemProvider(Provider):
    @provide(scope=Scope.APP)
    def get_session(self) -> aioboto3.Session:
        return aioboto3.Session()
    
    @provide(scope=Scope.APP)
    def get_factory(self, session: aioboto3.Session) -> MinioClientFactory:
        return MinioClientFactory()

    @provide(scope=Scope.APP)
    async def get_s3_client(self, factory: MinioClientFactory) -> AsyncIterator[S3Client]:
        async with factory.get_minio_client() as client:
            try:
                await client.head_bucket(Bucket=settings.minio.FILE_BUCKET_NAME)
            except ClientError as e:
                if e.response['Error']['Code'] == '404':
                    await client.create_bucket(Bucket=settings.minio.FILE_BUCKET_NAME)
                else:
                    raise e
            yield client
    
    @provide(scope=Scope.REQUEST)
    async def AwsRepo(self, client: S3Client) -> IAwsService:
        return MinioFileService(client = client)