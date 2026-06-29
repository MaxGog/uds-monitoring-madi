from backend.config.config import settings

from minio import Minio


minio_client = Minio(
    endpoint = settings.minio.MINIO_ENDPOINT,
    access_key = settings.minio.MINIO_ADMIN,
    secret_key = settings.minio.MINIO_PASS,
    secure = settings.minio.MINIO_SSL,
)

