from dishka import Provider, Scope, provide
from minio import Minio
from backend.config.config import settings
from backend.core.db.aws.minio_conn import minio_client
class FilesystemProvider(Provider):
    @provide(scope=Scope.APP)
    def MinIO(self) -> Minio:
        client = minio_client
        if not client.bucket_exists(settings.minio.FILE_BUCKET_NAME):
            client.make_bucket(settings.minio.FILE_BUCKET_NAME)
        return client