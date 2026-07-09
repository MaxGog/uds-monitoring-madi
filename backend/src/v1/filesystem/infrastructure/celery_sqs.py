# import os
# import boto3
# from celery import Celery
# from redis import Redis
# from sqlalchemy import create_engine
# from sqlalchemy.orm import sessionmaker
# import uuid6

# from backend.config.config import settings
# from backend.core.db.postgres.data_orms.document_orm import Document

# celery_app = Celery('sync_tasks', broker='redis://localhost:6379/0')

# # Нужны синхронные варианты
# minio_client = boto3.client(
#     "s3",
#     endpoint_url=settings.minio.MINIO_ENDPOINT,
#     aws_access_key_id=settings.minio.MINIO_ADMIN,
#     aws_secret_access_key=settings.minio.MINIO_PASS,
# )
# engine = create_engine(settings.db.DB_SYNC_URL)
# SessionLocal = sessionmaker(bind=engine)

# @celery_app.task(name="process_document_upload", max_retries=3, default_retry_delay=5)
# def process_document_upload_task(payload: dict, uploader_id_str: str):
#     """
#     Асинхронная задача: вычитывает метаданные из MinIO и сохраняет запись в БД
#     """
#     bucket = payload["s3_bucket"]
#     key = payload["s3_key"]
    
#     try:
#         # 1. Запрашиваем информацию о файле напрямую у MinIO
#         response = minio_client.head_object(Bucket=bucket, Key=key)
        
#         # Разделяем имя, чтобы получить расширение/тип (.pdf, .docx)
#         size = response["ContentLength"]
#         content_type = response["ContentType"]
#         checksum = response["ETag"].strip('"') if response.etag else None
#         file_ext = os.path.splitext(payload["name"])[1].lower().replace(".", "")

#         # 2. Создаем запись в базе данных
#         db_document = Document(
#             id=uuid6.uuid7(),
#             name=payload["name"],
#             size_bytes=response.size,
#             checksum_sha256=checksum, 
#             file_type=file_ext,
#             s3_bucket=bucket,
#             s3_key=key,
#             content_type=payload["content_type"] or response.content_type,
#             uploader_id=uuid6.UUID(uploader_id_str),
#             owner_type=payload["owner_type"],
#             owner_id=payload["owner_id"]
#         )
        
#         with SessionLocal() as session:
#             session.add(db_document)
#             session.commit()
            
#         return {"status": "success", "document_id": str(db_document.id)}

#     except Exception as e:
#         # Если файл еще не до конца загрузился, Celery попробует снова через пару секунд
#         raise process_document_upload_task.retry(exc=e)