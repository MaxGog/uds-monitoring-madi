from dataclasses import dataclass
import logging
from typing import List, Optional
from uuid import UUID

from fastapi import HTTPException, status
import uuid6

from backend.core.db.postgres.data_orms.document_orm import Document, DocumentOwnerType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases
from backend.config.config import settings
from backend.src.v1.filesystem.infrastructure.celery_sqs import process_document_upload_task
from backend.src.v1.filesystem.presentation.dtos import ConfirmUploadRequest, DocumentResponse, DocumentUpdateRequest, GetUploadUrlRequest

logger = logging.getLogger(__file__)

@dataclass
class FsUsecases(IFsUsecases):
    uow: IUnitOfWork
    aws_service: IAwsService
    file_repo: IFileRepo
    user_repo: IUserRepo

    # --- ГЕНЕРАЦИЯ ССЫЛКИ ДЛЯ PUT-ЗАПРОСА ---
    async def initiate_upload(self, uploader_id: UUID, data: GetUploadUrlRequest) -> dict:
        try:
            # Генерируем уникальный s3_key на базе UUIDv7, сохраняя оригинальное расширение
            file_ext = data.name.split(".")[-1] if "." in data.name else "bin"
            owner_folder = data.owner_type.value if hasattr(data.owner_type, 'value') else str(data.owner_type)
            unique_key = f"{owner_folder or 'common'}/{uuid6.uuid7()}.{file_ext}"
            upload_url = await self.aws_service.generate_upload_url(content_type = data.content_type, s3_key = unique_key, uploader_id = uploader_id, owner_type=data.owner_type, owner_id = data.owner_id)
            
            return {
                "upload_url": upload_url,
                "s3_bucket": settings.minio.FILE_BUCKET_NAME,
                "s3_key": unique_key
            }
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- ОПОВЕЩЕНИЕ О ЗАГРУЗКЕ (ОТПРАВКА В CELERY) ---
    async def confirm_upload(self, data: ConfirmUploadRequest, uploader_id: UUID) -> dict:
        # Отправляем задачу в Celery.
        try:
            process_document_upload_task.delay(
                payload=data.model_dump(),
                uploader_id_str=str(uploader_id)
            )
            return {"message": "File processing dispatched to queue"}
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- READ ---
    async def get_document_download_link(self, item_id: UUID) -> str:
        try:
            async with self.uow as uow:
                doc = await uow.file_repo.get_by_id(item_id)
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found")
                    
                # Возвращаем временную безопасную ссылку на чтение файла
                return await self.aws_service.generate_download_url(doc.s3_bucket, doc.s3_key)
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- PATCH ---
    async def update_document(self, document_id: UUID, update_data: DocumentUpdateRequest):
        try:
            async with self.uow as uow:
                document = await self.file_repo.get_by_id(document_id)
                if not document:
                    raise HTTPException(
                        status_code=status.HTTP_404_NOT_FOUND, 
                        detail=f"Document with id {document_id} not found"
                    )

                update_dict = update_data.model_dump(exclude_unset=True, exclude_none=True)

                if not update_dict:
                    return document

                if "name" in update_dict and update_dict["name"]:
                    update_dict["name"] = update_dict["name"].strip()

                # 4. Обновляем запись в базе данных через репозиторий
                for key, value in update_dict.items():
                        setattr(document, key, value)
                await uow.commit()

                updated_document = DocumentResponse.model_validate(document)
                return updated_document
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Error uploading document"
            )

    # --- DELETE ---
    async def delete_document(self, item_id: UUID) -> None:
        try:
            async with self.uow as uow:
                doc = await uow.file_repo.get_by_id(item_id)
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found")
                    
                # Удаляем физический файл из хранилища MinIO
                await self.aws_service.delete_object(doc.s3_bucket, doc.s3_key)
                
                # Удаляем метаданные из СУБД
                await uow.file_repo.delete(doc)
                await uow.commit()
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- ЧТЕНИЕ МЕТАДАННЫХ ОДНОГО ФАЙЛА ---
    async def get_file_by_id(self, item_id: UUID) -> DocumentResponse:
        try:
            async with self.uow as uow:
                doc = await uow.file_repo.get_by_id(item_id)
                if not doc:
                    raise HTTPException(status_code=404, detail="Document not found")
                return DocumentResponse.model_validate(doc)
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- ЧТЕНИЕ СПИСКА ФАЙЛОВ С ФИЛЬТРАЦИЕЙ ---
    async def get_files(self, owner_type: Optional[DocumentOwnerType] = None, owner_id: Optional[int] = None) -> List[DocumentResponse]:
        try:
            async with self.uow as uow:
                # Преобразуем Enum значение в строку для репозитория, если оно передано
                type_str = owner_type.value if owner_type else None
                
                docs = await uow.file_repo.get_all(owner_type=type_str, owner_id=owner_id)
                return [DocumentResponse.model_validate(d) for d in docs]
        except HTTPException as e:
            logger.error(e)
            raise e 
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # Ужасный тестовый метод, нужен дата класс, но мне влом
    async def register_uploaded_file(
        self,
        document_id: UUID,
        name: str,
        size_bytes: int,
        checksum_sha256: str,
        file_type: str,
        s3_bucket: str,
        s3_key: str,
        content_type: str,
        uploader_id: UUID | None,
        owner_type_str: str | None,
        owner_id: int | None
    ) -> None:
        try:
            async with self.uow as uow:
                owner_type_enum = None
                if owner_type_str:
                    try:
                        owner_type_enum = DocumentOwnerType(owner_type_str.lower())
                    except ValueError as e:
                        logger.error(e)
                        owner_type_enum = None
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

                # Сохраняем в базу данных
                await uow.file_repo.add(new_document)
                await uow.commit()
                logger.info(f"Документ {document_id} успешно зарегистрирован в БД через вебхук")

        except Exception as e:
            await uow.rollback()
            logger.error(f"Не удалось сохранить документ в базу данных: {e}")
            raise

    async def delete_file(self):
        pass