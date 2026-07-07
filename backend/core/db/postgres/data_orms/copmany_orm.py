from typing import List, Optional

from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from backend.core.db.postgres.base_orm import Base


class Company(Base):
    __tablename__ = "companies"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    inn: Mapped[Optional[str]] = mapped_column(String(20), nullable=True)

    kpp: Mapped[str] = mapped_column(String(20), nullable=True)
    address: Mapped[str] = mapped_column(String(500))
    
    # --- Конфиденциальные данные ---
    bank_account: Mapped[str] = mapped_column(String(30), nullable=True) # Р/с
    bank_name: Mapped[str] = mapped_column(String(255), nullable=True)
    bic: Mapped[str] = mapped_column(String(20), nullable=True) # БИК

    # Связи
    # Один-ко-многим: В компании много пользователей
    users: Mapped[List["User"]] = relationship(
        "User", 
        back_populates="company",
        cascade="all, delete-orphan"
    )