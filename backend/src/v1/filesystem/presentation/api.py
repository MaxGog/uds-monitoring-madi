import logging
from pathlib import Path
from typing import List, Optional
from urllib.parse import unquote
from uuid import UUID
import uuid

from fastapi import APIRouter, Depends, File, HTTPException, Query, Request, UploadFile, status
from dishka.integrations.fastapi import FromDishka, inject
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from types_aiobotocore_s3 import S3Client
import uuid6

from backend.core.db.postgres.data_orms.document_orm import DocumentOwnerType
from backend.core.db.postgres.data_orms.role_orm import ActionType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.role_models import EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
import httpx

from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFsUsecases
from backend.src.v1.filesystem.presentation.dtos import DocumentResponse, DocumentUpdateRequest, GetUploadUrlRequest, PresignedUrlResponse
from backend.config.config import settings

logger = logging.getLogger(__file__)

router = APIRouter()

@router.post("/upload-url", response_model=BaseResponse[PresignedUrlResponse])
@inject
async def request_upload_url(
    data: BaseRequest[GetUploadUrlRequest],
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.CREATE)),
):
    """Запрос presigned-ссылки для прямой загрузки файла в MinIO клиентом,
    автоматическое создание записи в postgresql через вебхук (альтернатива - реализовывать полноценную очередь и SQS)
    """
    try:
        user_id = user.get('sub')
        result = await uc.initiate_upload(uploader_id = user_id, data = data.data)
        return BaseResponse(data=result)
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.get("/{file_id}/download", response_model=BaseResponse[str])
@inject
async def get_download_url(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
):
    """Получение временной ссылки на скачивание/просмотр файла"""
    try:
        url = await uc.get_document_download_link(file_id)
        return BaseResponse(data=url)
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/", response_model=BaseResponse[List[DocumentResponse]])
@inject
async def get_documents(
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
    owner_type: Optional[DocumentOwnerType] = Query(
        None, 
        description="Фильтр по типу владельца файла (contract, act, object, work)"
    ),
    owner_id: Optional[int] = Query(
        None, 
        description="Идентификатор связанной сущности (например, ID договора)"
    ),
):
    try:
        result = await uc.get_files(owner_type=owner_type, owner_id=owner_id)
        return BaseResponse(data=result)
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get("/{file_id}", response_model=BaseResponse[DocumentResponse])
@inject
async def get_document_by_id(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.READ)),
):
    try:
        result = await uc.get_file_by_id(file_id)
        return BaseResponse(data=result)
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.patch("/{document_id}", response_model=BaseResponse[DocumentResponse])
@inject
async def patch_document(
    document_id: UUID,
    data: BaseRequest[DocumentUpdateRequest],
    uc: FromDishka[IFsUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.UPDATE)),
):
    try:
        result = await uc.update_document(
            document_id=document_id, 
            update_data=data.data
        )
        return BaseResponse(data=result)
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@router.delete("/{file_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_document(
    file_id: UUID,
    uc: FromDishka[IFsUsecases],
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.DELETE)),
):
    """Удаление файла из MinIO и чистка метаданных из БД"""
    try:
        await uc.delete_document(file_id)
        return
    except HTTPException as e:
        logger.error(e)
        raise e 
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


# Ужасный тестовый эндпоинт
@router.post("/webhook", status_code=status.HTTP_200_OK)
@inject
async def minio_webhook(
    event_data: dict,
    uow: FromDishka[IUnitOfWork],
    uc: FromDishka[IFsUsecases]
):
    """
    Эндпоинт, который MinIO вызывает сам сразу после успешного сохранения файла
    """
    try:
        result = await uc.process_minio_webhook(event_data)

        return {"status": "success", "result": str(result)}
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(f"Ошибка при обработке вебхука MinIO: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, 
            detail="Internal webhook processing error"
        )

@router.post("/upload-estimation", status_code=status.HTTP_202_ACCEPTED)
@inject
async def upload_estimation(
    uc: FromDishka[IFsUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.DOCUMENT, ActionType.CREATE)),
    file: UploadFile = File(...),
):
    '''
    Просто тестовый эндпоинт-пример подгрузки файла и его парсинг.
    '''
    try:
        user_id = current_user.get("sub")
        await uc.parse_excel(user_id = user_id, file = file)
        return
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

public_fs_router = APIRouter(prefix="/fss", tags=["Public Testing"])


@public_fs_router.get("/test-upload-ui", response_class=HTMLResponse)
async def test_upload_ui(
    request: Request
):
    try:
        BASE_DIR = Path(__file__).resolve().parent.parent.parent.parent.parent
        TEMPLATES_DIR = BASE_DIR / "templates"
        templates = Jinja2Templates(directory=str(TEMPLATES_DIR))
        print(templates)
        html_content =  TEMPLATES_DIR / "test_file_upload_ui.html"
        return templates.TemplateResponse(
        request=request,
        name="test_file_upload_ui.html",
        context={
            "request": request,
            # сюда можно передать дополнительные переменные, если пригодятся в HTML
        }
    )
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