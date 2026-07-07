from datetime import date, datetime
from enum import Enum
from typing import List, Optional
import uuid

from sqlalchemy import UUID, BigInteger, Date, DateTime, ForeignKey, Numeric, PrimaryKeyConstraint, String, Text, UniqueConstraint, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


from sqlalchemy import Enum as SqlEnum

from backend.core.db.postgres.base_orm import Base


class ContractType(str, Enum):
    '''
    Для различия того, кто выполняет работу
    '''
    GENERAL = "general"
    WORK = "work"
    ADDITIONAL_AGREEMENT = "additional"

class ContractStatus(str, Enum):
    DRAFT = "draft"
    ACTIVE = "active"
    COMPLETED = "completed"
    TERMINATED = "terminated"

class Contract(Base):
    '''
    Договор содержит в себе информацию о компании (не нашей), плановые даты и фактические, стомости

    '''
    __tablename__ = "contracts"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[Optional[String]] = mapped_column(String)
    date_signed: Mapped[date] = mapped_column(Date, nullable=True)
    description: Mapped[Optional[str]] = mapped_column(Text, nullable=True)
    status: Mapped[ContractStatus] = mapped_column(SqlEnum(ContractStatus), default=ContractStatus.DRAFT, nullable=True)
    type: Mapped[ContractType] = mapped_column(SqlEnum(ContractType), default=ContractType.GENERAL, nullable=True)

    cost: Mapped[str] = mapped_column(String(100), nullable=True)
    total_cost: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)

    planned_start: Mapped[date] = mapped_column(Date, nullable=True)
    planned_end: Mapped[date] = mapped_column(Date, nullable=True)
    actual_start: Mapped[Optional[date]] = mapped_column(Date, nullable=True)
    actual_end: Mapped[Optional[date]] = mapped_column(Date, nullable=True)

    # Ссылка на объект
    object_id: Mapped[Optional[int]] = mapped_column(ForeignKey("objects.id"), nullable=True)
    work_id: Mapped[Optional[int]] = mapped_column(ForeignKey("works.id"), nullable=True)
    
    # Связи обратно к сущностям
    items: Mapped[List["ContractItem"]] = relationship(
        "ContractItem", 
        back_populates="contract", 
        cascade="all, delete-orphan"
    )
    object: Mapped[Optional["Object"]] = relationship("Object", back_populates="contracts")
    work: Mapped[Optional["Work"]] = relationship("Work", back_populates="contracts")

class ContractItem(Base):
    '''
    Я не знаю бизнес и специфику и оттолкнусь от возможности сделать гибкую систему,
    так что эта сущность отражает лишь конкретную позицию в договоре.
    '''
    __tablename__ = "contract_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    contract_id: Mapped[int] = mapped_column(ForeignKey("contracts.id", ondelete="CASCADE"))
    
    title: Mapped[str] = mapped_column(String(255)) # Наименование обязательства/работы
    description: Mapped[Optional[str]] = mapped_column(Text)
    
    # Объемы и единица измерения
    quantity: Mapped[float] = mapped_column(Numeric(15, 3)) # Например, 150.5
    unit: Mapped[str] = mapped_column(String(20))          # Например, "м2", "шт", "пог.м"
    
    # Стоимость
    price_per_unit: Mapped[float] = mapped_column(Numeric(15, 2)) # Цена за единицу
    total_price: Mapped[float] = mapped_column(Numeric(15, 2))    # Итого по пункту (quantity * price)
    
    contract: Mapped["Contract"] = relationship("Contract", back_populates="items")