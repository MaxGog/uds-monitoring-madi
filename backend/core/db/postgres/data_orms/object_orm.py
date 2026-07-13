import enum
from typing import List

from sqlalchemy import Date, DateTime, Enum, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.db.postgres.base_orm import Base
from backend.src.v1.data.domain.models import ObjectStatus


class Object(Base):
    __tablename__ = "objects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))     #алиас для адреса. Например "Большой театр"
    address: Mapped[str] = mapped_column(String(500), nullable=True)
    district: Mapped[str] = mapped_column(String(100), nullable=True)  # Адм. округ
    status: Mapped[ObjectStatus] = mapped_column(Enum(ObjectStatus, name="object_status_enum", native_enum=True, values_callable=lambda x: [e.value for e in x]))
    # Внешние ключи на компании
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=True) # Надзорный орган
    contractor_id: Mapped[int] = mapped_column(ForeignKey("companies.id"), nullable=True) # Подрядчик
    
    supervisor: Mapped["Company"] = relationship("Company", foreign_keys=[supervisor_id])
    contractor: Mapped["Company"] = relationship("Company", foreign_keys=[contractor_id])
    
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="object")
    works: Mapped[List["Work"]] = relationship("Work", back_populates="object")

    acts: Mapped[List["Act"]] = relationship("Act", back_populates="object")