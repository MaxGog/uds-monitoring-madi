from datetime import date, datetime
from typing import List

from sqlalchemy import Date, DateTime, ForeignKey, Numeric, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship
from backend.core.db.postgres.base_orm import Base
from backend.core.db.postgres.data_orms.act_orm import WorkAct
from backend.core.db.postgres.data_orms.company_orm import Company
from backend.core.db.postgres.data_orms.contract_orm import Contract
from backend.core.db.postgres.data_orms.object_orm import Object


class Work(Base):
    '''
    Как я понимаю, у каждого объекта есть множество конкретных задач, т.е. работ.
    Работы перечислены, вероятно, в каждом excel документе как раз и представляют собой смету некую.
    В смете есть полная стоимость работ и сроки, а также статусы и ссылку на объект/договор.
    '''
    __tablename__ = "works"
    
    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column(String(255)) # Тип работы
    status: Mapped[str] = mapped_column(String(50))
    cost: Mapped[float] = mapped_column(Numeric(15, 2))
    deadline: Mapped[date] = mapped_column(Date)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)

    object_id: Mapped[int] = mapped_column(ForeignKey("objects.id"))
    object: Mapped["Object"] = relationship("Object", back_populates="works")

    contractor_id: Mapped[int] = mapped_column(ForeignKey("companies.id"))
    contractor: Mapped["Company"] = relationship("Company")

    contracts: Mapped[List["Contract"]] = relationship("Contract", back_populates="work")
    acts: Mapped[List["WorkAct"]] = relationship("WorkAct", back_populates="work")