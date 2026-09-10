from dataclasses import dataclass
import hashlib
import logging
import os
import shutil
from typing import List, Optional
from uuid import UUID
import uuid

from fastapi import HTTPException, UploadFile, status
from urllib.parse import quote, unquote, unquote_plus
import uuid6

from backend.core.db.postgres.data_orms.document_orm import Document, DocumentOwnerType
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileRepo, IFsUsecases
from backend.config.config import settings
from backend.src.v1.filesystem.presentation.dtos import ConfirmUploadRequest, DocumentResponse, DocumentUpdateRequest, GetUploadUrlRequest

logger = logging.getLogger(__file__)

# Допустимые форматы для Excel
ALLOWED_EXTENSIONS = {".xlsx", ".xls", ".xlsm"}
ALLOWED_CONTENT_TYPES = {
    "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",  # .xlsx
    "application/vnd.ms-excel",                                          # .xls
}

# Папка, куда временно сохраняем файлы перед отправкой в Celery
TEMP_UPLOAD_DIR = "./temp_uploads"
os.makedirs(TEMP_UPLOAD_DIR, exist_ok=True)

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
            owner_folder = data.owner_type.value if hasattr(data.owner_type, 'value') else str(data.owner_type) # type: ignore
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
                await self.aws_service.delete_object(doc.s3_bucket, doc.s3_key) # type: ignore
                
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
        owner_type: str | None,
        owner_id: int | None
    ) -> None:
        try:
            async with self.uow as uow:
                existing = await uow.file_repo.get_by_id(document_id)
                if existing:
                    logger.warning(f"Документ {document_id} уже зарегистрирован.")
                    return
                owner_type_enum = None
                if owner_type:
                    try:
                        owner_type_enum = DocumentOwnerType(owner_type.lower())
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
                    owner_type=owner_type_enum, 
                    owner_id=owner_id
                )

                # Сохраняем в базу данных
                await uow.file_repo.add(new_document)
                await uow.commit()
                logger.info(f"Документ {document_id} успешно зарегистрирован в БД через вебхук")

                # Отправка задачи
                excel_types = {"xlsx", "xls", "csv"}
                if file_type in excel_types:
                    from backend.src.v1.filesystem.infrastructure.parser_service.task import process_excel_import_task
                    await process_excel_import_task.kiq(document_id=str(document_id))
                    logger.info(f"Задача импорта Excel для {document_id} отправлена в Celery")

        except Exception as e:
            logger.error(f"Не удалось сохранить документ в базу данных: {e}")
            raise

    async def process_minio_webhook(self, event_data: dict) -> UUID | None:
        records = event_data.get("Records", [])
        if not records:
            logger.warning("Вебхук MinIO не содержит записей (Records)")
            return None

        record = records[0]
        s3_data = record.get("s3", {})

        s3_bucket = s3_data.get("bucket", {}).get("name")
        raw_s3_key = s3_data.get("object", {}).get("key")
        # unquote_plus корректно раскодирует и %XX, и '+' -> пробел
        s3_key = unquote_plus(raw_s3_key) if raw_s3_key else None

        if not s3_key:
            raise ValueError("В событии вебхука отсутствует S3-ключ (object.key)")

        size_bytes = s3_data.get("object", {}).get("size")
        content_type = s3_data.get("object", {}).get("contentType")
        etag = s3_data.get("object", {}).get("eTag", "").replace('"', '')

        raw_metadata = s3_data.get("object", {}).get("userMetadata", {})
        user_metadata = {k.lower(): v for k, v in raw_metadata.items()}

        def extract_meta(key: str) -> str | None:
            search_keys = [
                key.lower(),
                key.lower().replace("-", "_"),
                f"x-amz-meta-{key.lower()}",
                f"x-amz-meta-{key.lower()}".replace("-", "_")
            ]
            for k in search_keys:
                val = user_metadata.get(k)
                if val is not None:
                    val_str = str(val).strip()
                    if val_str.upper() in ("NULL", "NONE", ""):
                        return None
                    return val_str
            return None

        raw_uploader_id = extract_meta("uploader-id")
        raw_owner_type = extract_meta("owner-type")
        raw_owner_id = extract_meta("owner-id")
        raw_original_filename = extract_meta("original-filename")
        original_filename = unquote(raw_original_filename) if raw_original_filename else None

        uploader_id = UUID(raw_uploader_id) if raw_uploader_id else None
        owner_id = int(raw_owner_id) if raw_owner_id else None

        owner_type = None
        if raw_owner_type:
            try:
                owner_type = DocumentOwnerType(raw_owner_type.lower())
            except ValueError:
                logger.warning(
                    f"Неизвестный owner_type '{raw_owner_type}' в метаданных S3. "
                    f"Будет записано NULL. Допустимые значения: {[e.value for e in DocumentOwnerType]}"
                )
                owner_type = None

        # Ключ теперь строго вида estimations/{document_id}.{ext}
        key_filename = s3_key.split("/")[-1]           # "{document_id}.ext"
        file_type = key_filename.split(".")[-1].lower() if "." in key_filename else "bin"

        try:
            possible_uuid = key_filename.rsplit(".", 1)[0]
            document_id = UUID(possible_uuid)
        except (ValueError, IndexError):
            # На случай объектов, загруженных не через наш эндпоинт
            document_id = uuid6.uuid7()

        # Если оригинальное имя не пришло в метаданных (например, файл залит вручную) — fallback на ключ
        display_name = original_filename or key_filename

        await self.register_uploaded_file(
            document_id=document_id,
            name=display_name,
            size_bytes=size_bytes,
            checksum_sha256=etag,
            file_type=file_type,
            s3_bucket=s3_bucket,
            s3_key=s3_key,
            content_type=content_type,
            uploader_id=uploader_id,
            owner_type=owner_type,
            owner_id=owner_id
        )

        return document_id
    
    def is_excel_file(self, file: UploadFile) -> bool:
            """
            Проверяет, является ли файл Excel-таблицей по расширению и MIME-типу.
            """
            filename = file.filename or ""
            _, ext = os.path.splitext(filename.lower())
            
            # 1. Проверка по расширению
            if ext not in ALLOWED_EXTENSIONS:
                return False
                
            # 2. Проверка по MIME-типу (Content-Type)
            if file.content_type not in ALLOWED_CONTENT_TYPES:
                return False
                
            return True

    async def parse_excel(self, user_id: UUID, file):
        try:
            allowed_types = {
                "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                "application/vnd.ms-excel",
                "text/csv",
            }
            if file.content_type not in allowed_types:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Разрешены только файлы Excel (.xlsx, .xls, .csv)"
                )

            document_id = uuid6.uuid7()
            _, ext = os.path.splitext(file.filename or "")
            ext = ext.lower() or ".bin"

            s3_key = f"estimations/{document_id}{ext}"

            metadata = {
                "uploader-id": str(user_id),
                "owner-type": "contract",
                "owner-id": "123",
                "original-filename": quote(file.filename or "", safe=""),
            }

            try:
                await self.aws_service.upload_file(
                    file_obj=file.file,
                    s3_key=s3_key,
                    content_type=file.content_type,
                    metadata=metadata
                )
            except Exception as e:
                logger.error(f"Ошибка загрузки в S3: {e}")
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка загрузки в S3 хранилище: {str(e)}"
                )

            return {
                "status": "uploading",
                "document_id": document_id,
            }
        except Exception as e:
            logger.error(e)
            raise e