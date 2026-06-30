import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from dishka.integrations.fastapi import FromDishka, inject
from types_aiobotocore_s3 import S3Client
import uuid6

from backend.src.v1.filesystem.application.usecases import FsUsecases
from backend.src.v1.filesystem.domain.interfaces import IFsUsecases
from backend.src.v1.filesystem.presentation.dtos import UploadLinkRequest
from backend.config.config import settings

logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/files')
@inject
async def get_files(
    uc: FromDishka[IFsUsecases]
):
    # TODO сначала проверка прав доступа
    try:
        result = await uc.get_files()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {e}"
        )
    return result

@router.post('/upload')
@inject
async def upload_file(
    body: UploadLinkRequest,
    uc: FromDishka[IFsUsecases]
):
    """
    Генерирует временную PUT-ссылку для загрузки файла напрямую в MinIO.
    """
    # TODO сначала проверка прав доступа
    try :
        result = await uc.upload_file(body=body)
    except Exception as e:
        logger.error(f'Error generating presigned URL for UPLOAD: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {e}"
        )
    return result

@router.post("/test-direct-upload-to-minio", tags=["dev-tools"])
@inject
async def test_upload_to_minio(
    client: FromDishka[S3Client],
    file: UploadFile = File(...)
):
    """
    Эндпоинт исключительно для удобства тестирования в Swagger.
    Принимает файл через форму и загружает его в MinIO.
    """
    file_id = str(uuid6.uuid7())
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    s3_object_key = f"{file_id}.{extension}" if extension else file_id

    file_content = await file.read()

    # Напрямую загружаем в бакет какой то файл
    await client.put_object(
        Bucket=settings.minio.FILE_BUCKET_NAME,
        Key=s3_object_key,
        Body=file_content,
        ContentType=file.content_type
    )
    
    return {"status": "success", "s3_key": s3_object_key}

@router.get('/{file_id}')
@inject
async def generate_download_url(
    file_id: str,
    uc: FromDishka[IFsUsecases]
):
    # TODO сначала проверка прав доступа, потом поход в postgresql, потом получение ссылки в minio и проверяем наличие файла в minio, потом генерация ссылки на скачивание
    pass