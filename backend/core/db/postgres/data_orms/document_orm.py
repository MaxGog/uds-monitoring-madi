from datetime import datetime
from enum import Enum as PyEnum
from typing import Optional
from sqlalchemy import UUID, BigInteger, DateTime, Enum, Integer, Null, String, ForeignKey, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Enum as SqlEnum
import uuid6
from backend.core.db.postgres.base_orm import Base


class DocumentOwnerType(str, PyEnum):
    CONTRACT = "contract"
    ACT = "act"
    OBJECT = "object"
    WORK = "work"
    
# Таблица метаданных файлов и результатов парсинга
class Document(Base):
    __tablename__ = "documents"

    id: Mapped[uuid6.UUID] = mapped_column(
        UUID(as_uuid=True), 
        primary_key=True, 
        default=uuid6.uuid7
    )   
    # Метаданные файла
    name: Mapped[str] = mapped_column(String(255))
    size_bytes: Mapped[Optional[int]] = mapped_column(BigInteger)
    checksum_sha256: Mapped[Optional[str]] = mapped_column(Text)
    file_type: Mapped[Optional[str]] = mapped_column(Text)
    s3_bucket: Mapped[str] = mapped_column(String(100))
    s3_key: Mapped[str] = mapped_column(String(500))
    content_type: Mapped[str] = mapped_column(String(100))

    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    uploader_id: Mapped[uuid6.UUID] = mapped_column(ForeignKey("users.id"))
    uploader: Mapped["User"] = relationship("User")

    owner_type: Mapped[DocumentOwnerType] = mapped_column(SqlEnum(DocumentOwnerType), default=Null, nullable=True)
    owner_id: Mapped[int] = mapped_column(Integer, nullable=True) # ID сущности (Contract, Act, и т.д.)
    # Результаты парсинга (структурированные данные, пока не уверен как это будет реализовано на самом деле)
    #status: Mapped[str] = mapped_column(String(50), default="pending")
    #parsed_data: Mapped[dict | None] = mapped_column(JSON, nullable=True)

    # Получение всех документов для данного договора (сервис будущий)
    # @property
    # def documents(self):
    #     return session.query(Document).filter(
    #         Document.owner_type == DocumentOwnerType.CONTRACT,
    #         Document.owner_id == self.id
    #     ).all()