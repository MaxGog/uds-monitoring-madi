from typing import List

from fastapi import APIRouter, HTTPException, status
from dishka.integrations.fastapi import FromDishka, inject
import uuid6

from backend.src.v1.filesystem.application.usecases import FsUsecases
from backend.src.v1.filesystem.presentation.dtos import UploadLinkRequest
from backend.config.config import settings
router = APIRouter()

@router.get('files')
@inject
async def get_files(
    uc: FromDishka[FsUsecases]
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

@router.post('upload')
@inject
async def upload_file(
    body: UploadLinkRequest,
    uc: FromDishka[FsUsecases]
):
    """
    Генерирует временную PUT-ссылку для загрузки файла напрямую в MinIO.
    """
    # TODO сначала проверка прав доступа
    try :
        result = await uc.upload_file(bucket_name=settings.minio.FILE_BUCKET_NAME, body = body)
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate upload URL: {e}"
        )
    return result

@router.get('/{file_id}')
@inject
async def generate_download_url(
    file_id: str,
    uc: FromDishka[FsUsecases]
):
    # TODO сначала проверка прав доступа, потом поход в postgresql, потом получение ссылки в minio и проверяем наличие файла в minio, потом генерация ссылки на скачивание
    pass