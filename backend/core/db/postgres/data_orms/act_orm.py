from datetime import date
from enum import Enum
from typing import List, Optional

from sqlalchemy import Date, ForeignKey, Null, Numeric, String, Enum as SqlEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship


from backend.core.db.postgres.base_orm import Base
from backend.src.v1.data.domain.models import ActType, WorkActStatus

class WorkAct(Base):
    __tablename__ = "work_acts"

    id: Mapped[int] = mapped_column(primary_key=True)
    number: Mapped[str] = mapped_column(String(50))
    status: Mapped[WorkActStatus] = mapped_column(SqlEnum(WorkActStatus), default=WorkActStatus.DRAFT)
    date_signed: Mapped[date] = mapped_column(Date)
    type: Mapped[ActType] = mapped_column(SqlEnum(ActType), default=Null, nullable=True)
    
    # Ссылка на объект (для отчетности перед надзорным органом)
    object_id: Mapped[Optional[int]] = mapped_column(ForeignKey("objects.id"), nullable=True)
    # Ссылка на работу (для учета субподряда)
    work_id: Mapped[Optional[int]] = mapped_column(ForeignKey("works.id"), nullable=True)
    # Ссылка на контракт (для учета финансирования)
    contract_id: Mapped[Optional[int]] = mapped_column(ForeignKey("contracts.id"), nullable=True)

    object: Mapped[Optional["Object"]] = relationship("Object", back_populates="acts")
    work: Mapped[Optional["Work"]] = relationship("Work", back_populates="acts")
    contract: Mapped[Optional["Contract"]] = relationship("Contract", back_populates="acts")
    
    items: Mapped[List["WorkActItem"]] = relationship("WorkActItem", back_populates="act")

class WorkActItem(Base):
    __tablename__ = "work_act_items"

    id: Mapped[int] = mapped_column(primary_key=True)
    act_id: Mapped[int] = mapped_column(ForeignKey("work_acts.id", ondelete="CASCADE"))
    contract_item_id: Mapped[int] = mapped_column(ForeignKey("contract_items.id"))
    
    # Фактически выполненный объем в этом акте
    completed_quantity: Mapped[float] = mapped_column(Numeric(15, 3))
    
    act: Mapped["WorkAct"] = relationship("WorkAct", back_populates="items")
    contract_item: Mapped["ContractItem"] = relationship("ContractItem")