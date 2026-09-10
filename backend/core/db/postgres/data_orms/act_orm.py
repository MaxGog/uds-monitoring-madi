from datetime import date
from enum import Enum
from typing import List, Optional

from sqlalchemy import JSON, Date, ForeignKey, Null, Numeric, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.ext.hybrid import hybrid_property

from backend.core.db.postgres.base_orm import Base, TimestampMixin
from backend.src.v1.data.domain.models import ActType, ActStatus

class Act(Base, TimestampMixin):
    __tablename__ = "acts"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(50), nullable=True)
    status: Mapped[ActStatus] = mapped_column(SqlEnum(ActStatus), default=ActStatus.DRAFT)
    date_signed: Mapped[date] = mapped_column(Date, nullable=True)
    type: Mapped[ActType] = mapped_column(SqlEnum(ActType), default=Null, nullable=True)

    metadata_fields: Mapped[dict] = mapped_column(JSON, default={}, nullable=True)
    
    # Ссылка на объект (для отчетности перед надзорным органом)
    object_id: Mapped[Optional[int]] = mapped_column(ForeignKey("objects.id"), nullable=True)
    # Ссылка на работу (для учета субподряда)
    work_id: Mapped[Optional[int]] = mapped_column(ForeignKey("works.id"), nullable=True)
    # Ссылка на контракт (для учета финансирования)
    contract_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contracts.id"), nullable=True)

    object: Mapped[Optional["Object"]] = relationship("Object", back_populates="acts")
    work: Mapped[Optional["Work"]] = relationship("Work", back_populates="acts")
    contract: Mapped[Optional["Contract"]] = relationship("Contract", back_populates="acts")
    
    items: Mapped[List["ActItem"]] = relationship("ActItem", back_populates="act")

    @hybrid_property
    def total_amount(self) -> float:
        return sum((item.completed_quantity or 0.0) * (item.price or 0.0) for item in self.items)

class ActItem(Base):
    __tablename__ = "act_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("acts.id", ondelete="CASCADE"), nullable=True)
    contract_item_id: Mapped[int] = mapped_column(ForeignKey("contract_items.id"), nullable=True)
    
    # Фактически выполненный объем в этом акте
    completed_quantity: Mapped[float] = mapped_column(Numeric(15, 3), nullable=True)
    price: Mapped[float] = mapped_column(Numeric(15, 2), nullable=True)
    
    act: Mapped["Act"] = relationship("Act", back_populates="items")
    contract_item: Mapped["ContractItem"] = relationship("ContractItem")