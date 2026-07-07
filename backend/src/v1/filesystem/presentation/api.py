import logging

from fastapi import APIRouter, File, HTTPException, Query, UploadFile, status
from dishka.integrations.fastapi import FromDishka, inject
from types_aiobotocore_s3 import S3Client
import uuid6
from backend.core.db.postgres.data_orms.user_orm import FileAccessType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.presentation.api import CurrentUserPayload
import httpx

from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileAuthUsecases, IFsUsecases
from backend.src.v1.filesystem.presentation.dtos import UploadLinkRequest
from backend.config.config import settings

logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/files')
@inject
async def get_files(
    payload: CurrentUserPayload,
    uc: FromDishka[IFsUsecases],
    limit: int = Query(default=50, ge=1, le=100),
    offset: int = Query(default=0, ge=0),
):
    user_id = payload.get('sub')
    try:
        result = await uc.get_files(user_id = user_id, required_action = FileAccessType.READ)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {e}"
        )
    return result

@router.get('/{file_id}')
@inject
async def generate_download_url(
    file_id: str,
    payload: CurrentUserPayload,
    auth_uc: FromDishka[IFileAuthUsecases],
    uc: FromDishka[IFsUsecases],
):
    user_id = payload.get('sub')
    try:
        result = await uc.get_file(user_id, file_id = file_id)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get files: {e}"
        )
    return result

@router.post("/generate-upload-url")
@inject
async def get_upload_url(
    body: UploadLinkRequest,
    payload: CurrentUserPayload,
    uc: FromDishka[IFsUsecases]
):
    """
    Генерирует временную PUT-ссылку для загрузки файла в MinIO.
    """
    user_id = payload.get('sub')
    try:
        result = await uc.generate_upload_url(user_id = user_id, body = body)
    except Exception as e:
        print(e)
        logger.error(f'Error generating presigned URL for UPLOAD: {e}')
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL"
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

@router.post("/test-presigned-upload", tags=['dev-tools'])
@inject
async def test_presigned_upload(
    uow: FromDishka[IUnitOfWork],
    file: UploadFile = File(...),
    aws_service: FromDishka[IAwsService] = None,
):
    """
    Тестовый эндпоинт: имитирует поведение фронтенда.
    1. Генерирует временную PUT-ссылку.
    2. Через асинхронный HTTP-клиент загружает файл по этой ссылке в MinIO.
    """
    bucket_name = settings.minio.FILE_BUCKET_NAME
    # 1: Формируем параметры для генерации ссылки
    file_id = str(uuid6.uuid7())
    extension = file.filename.split(".")[-1] if "." in file.filename else ""
    object_key = f"{file_id}.{extension}" if extension else file_id
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
    # Передаём в бд
    try:
        async with uow:
            await uow.file_repo.create_file(
                id=file_id,
                user_id = '019f17ea-a900-7fe9-b66f-43d82725afca',
                name=file.filename, 
                content_type=content_type, 
                s3_key=object_key
            )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Файл загружен в MinIO, но произошла ошибка записи в БД: {str(e)}"
        )

    return {
        "status": "success",
        "message": "Цикл обработки полностью завершен",
        "database_record": {
            "id": file_id,
            "filename": file.filename,
            "s3_key": object_key
        },
        "used_link": upload_url
    }