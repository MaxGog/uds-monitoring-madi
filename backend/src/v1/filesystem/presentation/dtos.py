from datetime import datetime
from typing import Optional
from uuid import UUID
from pydantic import BaseModel, ConfigDict, Field

from backend.core.db.postgres.data_orms.document_orm import DocumentOwnerType


# --- ЗАПРОС НА ПОЛУЧЕНИЕ ССЫЛКИ ДЛЯ ЗАГРУЗКИ ---
class GetUploadUrlRequest(BaseModel):
    name: str = Field(..., max_length=255, description="Имя файла с расширением (image.png)")
    content_type: str = Field(..., max_length=100, description="MIME-тип (application/pdf)")
    owner_type: Optional[DocumentOwnerType] = Field(None)
    owner_id: Optional[int] = Field(None)

# --- ОТВЕТ С ССЫЛКОЙ ДЛЯ КЛИЕНТА ---
class PresignedUrlResponse(BaseModel):
    upload_url: str = Field(..., description="Прямая ссылка для PUT-запроса в MinIO")
    s3_bucket: str
    s3_key: str

# Используется для сохранения в БД после успешной загрузки в S3
class DocumentCreateRequest(BaseModel):
    name: str
    content_type: str
    s3_bucket: str
    s3_key: str
    size_bytes: int
    checksum_sha256: str
    owner_type: Optional[DocumentOwnerType] = None
    owner_id: Optional[int] = None

# ДОПОЛНЕНО: Используется для PATCH-запроса (например, переименование файла)
class DocumentUpdateRequest(BaseModel):
    name: Optional[str] = None
    owner_type: Optional[DocumentOwnerType] = None
    owner_id: Optional[int] = None

#--- СИГНАЛ ОБ УСПЕШНОЙ ЗАГРУЗКЕ (ДЛЯ ТРИГГЕРА CELERY и Вебхука) ---
class ConfirmUploadRequest(BaseModel):
    name: str
    s3_bucket: str
    s3_key: str
    content_type: str
    owner_type: Optional[DocumentOwnerType] = None
    owner_id: Optional[int] = None

# --- ОТВЕТ С МЕТАДАННЫМИ ИЗ БД ---
class DocumentResponse(BaseModel):
    id: UUID
    name: str
    size_bytes: Optional[int]
    checksum_sha256: Optional[str]
    file_type: Optional[str]
    s3_bucket: str
    s3_key: str
    content_type: str
    uploader_id: UUID
    owner_type: Optional[DocumentOwnerType]
    owner_id: Optional[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)