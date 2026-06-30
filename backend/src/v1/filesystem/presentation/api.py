import logging
from typing import List

from fastapi import APIRouter, File, HTTPException, UploadFile, status
from dishka.integrations.fastapi import FromDishka, inject
from types_aiobotocore_s3 import S3Client
import uuid6
import httpx

from backend.src.v1.filesystem.application.usecases import FsUsecases
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFsUsecases
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


@router.post("/test-presigned-upload")
@inject
async def test_presigned_upload(
    file: UploadFile = File(...),
    aws_service: FromDishka[IAwsService] = None
):
    """
    Тестовый эндпоинт: имитирует поведение фронтенда.
    1. Генерирует асинshared временную PUT-ссылку.
    2. Через асинхронный HTTP-клиент загружает файл по этой ссылке в MinIO.
    """
    # 1: Формируем параметры для генерации ссылки
    bucket_name = settings.minio.FILE_BUCKET_NAME
    object_key = f"test_{file.filename}"
    content_type = file.content_type

    try:
        upload_url = await aws_service.generate_url(
            ClientMethod="put_object",
            Params={
                "Bucket": bucket_name,
                "Key": object_key,
                "ContentType": content_type
            },
            ExpiresIn=300
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Ошибка генерации Presigned URL: {str(e)}"
        )

    file_bytes = await file.read()

    # 2: Имитируем фронтенд — делаем PUT запрос на полученный URL
    async with httpx.AsyncClient() as http_client:
        response = await http_client.put(
            upload_url,
            content=file_bytes,
            headers={"Content-Type": content_type}
        )

    if response.status_code != 200:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "msg": "MinIO отклонил загрузку по Presigned URL",
                "minio_response": response.text,
                "attempted_url": upload_url
            }
        )

    return {
        "status": "success",
        "message": "Файл успешно загружен через Presigned URL",
        "s3_key": object_key,
        "used_presigned_url": upload_url
    }

@router.get('/{file_id}')
@inject
async def generate_download_url(
    file_id: str,
    uc: FromDishka[IFsUsecases]
):
    # TODO сначала проверка прав доступа, потом поход в postgresql, потом получение ссылки в minio и проверяем наличие файла в minio, потом генерация ссылки на скачивание
    pass