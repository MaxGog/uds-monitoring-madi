import logging
from pathlib import Path
from typing import List, Optional
from uuid import UUID

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status
from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import FileResponse, HTMLResponse
from types_aiobotocore_s3 import S3Client
import uuid6

from backend.core.db.postgres.data_orms.document_orm import Document, DocumentOwnerType
from backend.core.db.postgres.data_orms.role_orm import ActionType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.role_models import EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.filesystem.application.file_uc import FsUsecases
import httpx

from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFsUsecases
from backend.src.v1.filesystem.presentation.dtos import ConfirmUploadRequest, DocumentResponse, GetUploadUrlRequest, PresignedUrlResponse
from backend.config.config import settings

logger = logging.getLogger(__file__)

router = APIRouter()

@router.post("/request-upload", response_model=BaseResponse[PresignedUrlResponse])
@inject
async def request_upload_url(
    data: BaseRequest[GetUploadUrlRequest],
    uc: FromDishka[IFsUsecases],
    #scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.CREATE)),
):
    """Шаг 1: Запрос presigned-ссылки для прямой загрузки файла в MinIO клиентом"""
    try:
        result = await uc.initiate_upload(data.data)
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

# @router.post("/confirm-upload", status_code=status.HTTP_202_ACCEPTED)
# @inject
# async def confirm_upload(
#     data: BaseRequest[ConfirmUploadRequest],
#     uc: FromDishka[IFsUsecases],
#     user: CurrentUserPayload,
# ):
#     """Шаг 2: Сигнал о том, что клиент залил файл. Ставит задачу в Celery для внесения в БД"""
#     try:
#         uploader_id: UUID = user.get('sub')
#         result = await uc.confirm_upload(data.data, uploader_id)
#         return BaseResponse(data=result)
#     except Exception as e:
#         logger.error(e)
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get("/{file_id}/download-url", response_model=BaseResponse[str])
@inject
async def get_download_url(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    #scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
):
    """Получение временной ссылки на скачивание/просмотр файла"""
    try:
        url = await uc.get_document_download_link(file_id)
        return BaseResponse(data=url)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_document(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    #scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.DELETE)),
):
    """Удаление файла из MinIO и чистка метаданных из БД"""
    try:
        await uc.delete_document(file_id)
        return
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.get("/", response_model=BaseResponse[List[DocumentResponse]])
@inject
async def get_documents(
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    #scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
    owner_type: Optional[DocumentOwnerType] = Query(
        None, 
        description="Фильтр по типу владельца файла (contract, act, object, work)"
    ),
    owner_id: Optional[int] = Query(
        None, 
        description="Идентификатор связанной сущности (например, ID договора)"
    ),
):
    """
    Получение списка метаданных всех файлов из PostgreSQL.
    
    Примеры использования:
    - GET /documents -> все файлы в системе
    - GET /documents?owner_type=contract&owner_id=12 -> все файлы договора с OWNER ID 12
    - GET /documents?owner_type=object&owner_id=5 -> все файлы строительного объекта с OWNER ID 5
    """
    result = await uc.get_files(owner_type=owner_type, owner_id=owner_id)
    return BaseResponse(data=result)


@router.get("/{file_id}", response_model=BaseResponse[DocumentResponse])
@inject
async def get_document_by_id(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    #scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
):
    """
    Получение метаданных конкретного файла по его UUID из PostgreSQL
    (размер, контрольная сумма, тип контента, дата загрузки и т.д.)
    """
    result = await uc.get_file_by_id(file_id)
    return BaseResponse(data=result)

@router.post("/webhook", status_code=status.HTTP_200_OK)
@inject
async def minio_webhook(
    payload: dict,
    uow: FromDishka[IUnitOfWork],
):
    """
    Эндпоинт, который MinIO вызывает САМ сразу после успешного сохранения файла
    """
    records = payload.get("Records", [])
    if not records:
        return {"status": "skipped"}
        
    event = records[0]
    # Фильтруем системные тестовые события MinIO (s3:TestEvent)
    if "ObjectCreated" not in event.get("eventName", ""):
        return {"status": "skipped"}

    s3_data = event["s3"]
    s3_object = s3_data["object"]
    user_meta = s3_object.get("userMetadata", {})

    # Извлекаем данные, которые мы зашили на этапе генерации Presigned URL
    uploader_id = user_meta.get("X-Amz-Meta-Uploader-Id")
    owner_type = user_meta.get("X-Amz-Meta-Owner-Type")
    owner_id = user_meta.get("X-Amz-Meta-Owner-Id")
    
    s3_key = s3_object["key"]
    file_name = s3_key.split("/")[-1]
    file_ext = file_name.split(".")[-1] if "." in file_name else None

    async with uow:
        new_doc = Document(
            id=uuid6.uuid7(),
            name=file_name,
            size_bytes=s3_object.get("size"),
            checksum_sha256=s3_object.get("eTag", "").strip('"'),
            file_type=file_ext,
            s3_bucket=s3_data["bucket"]["name"],
            s3_key=s3_key,
            content_type=s3_object.get("contentType"),
            uploader_id=uuid6.UUID(uploader_id) if uploader_id else None,
            owner_type=owner_type,
            owner_id=int(owner_id) if owner_id else None
        )
        await uow.file_repo.add(new_doc)
        await uow.commit()

    return {"status": "success", "document_id": str(new_doc.id)}


@router.get("/test-upload-ui", response_class=HTMLResponse)
async def test_upload_ui():
    try:
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
        TEMPLATES_DIR = BASE_DIR / "templates"
        html_content =  TEMPLATES_DIR / "test_file_upload_ui.html"
        return FileResponse(html_content)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

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