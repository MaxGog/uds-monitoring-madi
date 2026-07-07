import enum
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.db.postgres.base_orm import Base


class ObjectStatus(str, enum.Enum):
    PENDING = 'pending'
    ACCEPTED = 'accepted'
    IN_PROGRESS = 'in_progress'
    COMPLETED = 'completed'
    PAUSED = 'paused'
    CANCELLED = 'cancelled'
    EXPIRED = 'expired'
    FAILED = 'failed'

class Object(Base):
    __tablename__ = "objects"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255))     #алиас для адреса. Например "Большой театр"
    address: Mapped[str] = mapped_column(String(500))
    district: Mapped[str] = mapped_column(String(100))  # Адм. округ
    
    # Внешние ключи на компании
    supervisor_id: Mapped[int] = mapped_column(ForeignKey("companies.id")) # Надзорный орган
    contractor_id: Mapped[int] = mapped_column(ForeignKey("companies.id")) # Подрядчик
    
    supervisor: Mapped["Company"] = relationship("Company", foreign_keys=[supervisor_id])
    contractor: Mapped["Company"] = relationship("Company", foreign_keys=[contractor_id])
    
    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="object")
    works: Mapped[List["Work"]] = relationship("Work", back_populates="object")

    # Сумма по всем актам, которые привязаны к объекту напрямую или через работы
    # Опасный кусок кода, т.к. при огромных объёмах данных может просто сдохнуть БД из-за нехватки ОЗУ. Решение - ограничить кол-во данных и выбрать конкретные поля.
    # Также можно сделать парсер и CRON операцию по анализу данных через Pandas и в отдельные поля/таблицы вносить итоги.
    @property
    def total_completed_cost(self):
        return sum(act.total_amount for act in self.acts)