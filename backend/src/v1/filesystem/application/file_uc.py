from dataclasses import dataclass
from datetime import timedelta
import logging
from typing import List, Optional
import uuid

from fastapi import HTTPException, status
import uuid6

from backend.core.db.postgres.data_orms.document_orm import Document, DocumentOwnerType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases
from backend.config.config import settings
from backend.src.v1.filesystem.infrastructure.celery_sqs import process_document_upload_task
from backend.src.v1.filesystem.presentation.dtos import ConfirmUploadRequest, DocumentResponse, GetUploadUrlRequest

logger = logging.getLogger(__file__)

@dataclass
class FsUsecases(IFsUsecases):
    uow: IUnitOfWork
    aws_service: IAwsService
    file_repo: IFileRepo
    user_repo: IUserRepo

    # --- ШАГ 1: ГЕНЕРАЦИЯ ССЫЛКИ ДЛЯ PUT-ЗАПРОСА ---
    async def initiate_upload(self, uploader_id: uuid.UUID, data: GetUploadUrlRequest) -> dict:
        try:
            # Генерируем уникальный s3_key на базе UUIDv7, сохраняя оригинальное расширение
            file_ext = data.name.split(".")[-1] if "." in data.name else "bin"
            unique_key = f"{data.owner_type or 'common'}/{uuid6.uuid7()}.{file_ext}"
            
            upload_url = await self.aws_service.generate_upload_url(content_type = data.content_type, s3_key = unique_key, uploader_id = uploader_id, owner_type=data.owner_type, owner_id = data.owner_id)
            
            return {
                "upload_url": upload_url,
                "s3_bucket": settings.minio.FILE_BUCKET_NAME,
                "s3_key": unique_key
            }
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- ШАГ 2: ОПОВЕЩЕНИЕ О ЗАГРУЗКЕ (ОТПРАВКА В CELERY) ---
    async def confirm_upload(self, data: ConfirmUploadRequest, uploader_id: uuid.UUID) -> dict:
        # Отправляем задачу в Celery. Запись в БД появится асинхронно воркером
        process_document_upload_task.delay(
            payload=data.model_dump(),
            uploader_id_str=str(uploader_id)
        )
        return {"message": "File processing dispatched to queue"}

    # --- READ ---
    async def get_document_download_link(self, item_id: uuid.UUID) -> str:
        async with self.uow as uow:
            doc = await uow.file_repo.get_by_id(item_id)
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
                
            # Возвращаем временную безопасную ссылку на чтение файла
            return await self.aws_service.generate_download_url(doc.s3_bucket, doc.s3_key)

    # --- DELETE ---
    async def delete_document(self, item_id: uuid.UUID) -> None:
        async with self.uow as uow:
            doc = await uow.file_repo.get_by_id(item_id)
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
                
            # Удаляем физический файл из хранилища MinIO
            self.aws_service.delete_object(doc.s3_bucket, doc.s3_key)
            
            # Удаляем метаданные из СУБД
            await uow.file_repo.delete(doc)
            await uow.commit()

    # --- ЧТЕНИЕ МЕТАДАННЫХ ОДНОГО ФАЙЛА ---
    async def get_file_by_id(self, item_id: uuid.UUID) -> DocumentResponse:
        async with self.uow as uow:
            doc = await uow.file_repo.get_by_id(item_id)
            if not doc:
                raise HTTPException(status_code=404, detail="Document not found")
            return DocumentResponse.model_validate(doc)

    # --- ЧТЕНИЕ СПИСКА ФАЙЛОВ С ФИЛЬТРАЦИЕЙ ---
    async def get_files(self, owner_type: Optional[DocumentOwnerType] = None, owner_id: Optional[int] = None) -> List[DocumentResponse]:
        async with self.uow as uow:
            # Преобразуем Enum значение в строку для репозитория, если оно передано
            type_str = owner_type.value if owner_type else None
            
            docs = await uow.file_repo.get_all(owner_type=type_str, owner_id=owner_id)
            return [DocumentResponse.model_validate(d) for d in docs]


    # Ужасный тестовый метод    
    async def register_uploaded_file(
        self,
        document_id: uuid.UUID,
        name: str,
        size_bytes: int,
        checksum_sha256: str,
        file_type: str,
        s3_bucket: str,
        s3_key: str,
        content_type: str,
        uploader_id: uuid.UUID | None,
        owner_type_str: str | None,
        owner_id: int | None
    ) -> None:
        try:
            async with self.uow as uow:
                owner_type_enum = None
                if owner_type_str:
                    try:
                        # Приводим к верхнему регистру на случай расхождений
                        owner_type_enum = DocumentOwnerType(owner_type_str.upper())
                    except ValueError:
                        logger.warning(f"Получен неизвестный тип владельца: {owner_type_str}. Будет записан NULL.")
                        owner_type_enum = None

                # Создаем модель SQLAlchemy (замените на название вашего класса модели)
                new_document = Document(
                    id=document_id,
                    name=name,
                    size_bytes=size_bytes,
                    checksum_sha256=checksum_sha256,
                    file_type=file_type,
                    s3_bucket=s3_bucket,
                    s3_key=s3_key,
                    content_type=content_type,
                    uploader_id=uploader_id,
                    owner_type=owner_type_enum,  # Сюда уходит Либо Член Enum, либо чистый Python None
                    owner_id=owner_id            # Сюда уходит Либо int, либо чистый Python None
                )

                # Сохраняем в базу данных через вашу сессию
                await uow.file_repo.add(new_document)
                await uow.commit()
                logger.info(f"Документ {document_id} успешно зарегистрирован в БД через вебхук")

        except Exception as e:
            await uow.rollback()
            logger.error(f"Не удалось сохранить документ в базу данных: {e}")
            raise