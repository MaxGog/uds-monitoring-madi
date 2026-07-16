import asyncio
import logging
import os
from sqlalchemy import select

from backend.core.db.postgres.data_orms.document_orm import Document

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.core.tasks.broker import broker
from backend.src.v1.filesystem.domain.interfaces import IAwsService
from backend.src.v1.filesystem.infrastructure.parser_service.db_importer import DatabaseImporter
from backend.src.v1.filesystem.infrastructure.parser_service.excel_parser import ExcelParser
from dishka.integrations.taskiq import inject, FromDishka

logger = logging.getLogger(__file__)

@broker.task
@inject(patch_module=True)
async def process_excel_import_task(
    document_id: str,
    uow: FromDishka[IUnitOfWork],
    db_importer: FromDishka[DatabaseImporter],
    aws_service: FromDishka[IAwsService],
) -> None:
    # 1. Достаём путь к файлу в S3
    
    async with uow:
        stmt = select(Document).where(Document.id == document_id)
        result = await uow.session.execute(stmt)
        document = result.scalar_one_or_none()
        if not document:
            raise ValueError(f"Документ {document_id} не найден")
        s3_key = document.s3_key

    # 2. Скачиваем файл из MinIO на диск воркера
    logger.info(s3_key)
    logger.info(document_id)
    local_temp_path = await aws_service.download_file(s3_key)

    try:
        # 3. Парсим
        parser = ExcelParser(file_path=local_temp_path)
        parsed_objects = parser.parse()

        # 4. Пишем в БД
        await db_importer.import_data(parsed_objects)

    finally:
        if os.path.exists(local_temp_path):
            os.remove(local_temp_path)