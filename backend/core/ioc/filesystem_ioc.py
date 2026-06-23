from dishka import Provider, Scope, provide
from minio import Minio
from backend.config.config import settings

class FilesystemProvider(Provider):
    @provide(scope=Scope.APP)
    def MinIO(self) -> Minio:
        client = Minio(
            endpoint=settings.minio.MINIO_ENDPOINT,
            access_key=settings.minio.MINIO_ADMIN,
            secret_key=settings.minio.MINIO_PASS,
            secure=settings.minio.MINIO_SSL,
        )

        if not client.bucket_exists(settings.minio.CHAT_BUCKET_NAME):
            client.make_bucket(settings.minio.CHAT_BUCKET_NAME)
        return client