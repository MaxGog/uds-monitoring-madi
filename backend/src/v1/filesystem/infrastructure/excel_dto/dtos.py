# app/schemas/import_schemas.py
from datetime import date, datetime
from typing import List, Optional, Any
from pydantic import BaseModel, Field, field_validator


class ContractItemDTO(BaseModel):
    """Спецификация к договору"""
    title: str
    quantity: float
    unit: str
    price_per_unit: float
    total_price: Optional[float] = None

    @field_validator("quantity", "price_per_unit", "total_price", mode="before")
    @classmethod
    def clean_numeric(cls, v) -> float:
        if v is None or str(v).strip() == "":
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        # Очистка строк вроде "15 000,50 руб." -> "15000.50"
        cleaned = str(v).replace(" ", "").replace(",", ".").replace("\xa0", "").strip()
        cleaned = "".join(c for c in cleaned if c.isdigit() or c in ".-")
        return float(cleaned) if cleaned else 0.0

    def model_post_init(self, __context: Any) -> None:
        # Авторасчет стоимости позиции, если она не заполнена в Excel
        if not self.total_price:
            self.total_price = round(self.quantity * self.price_per_unit, 2)


class ContractDTO(BaseModel):
    """Договор по работе"""
    contract_id: Optional[str] = None
    date_signed: Optional[date] = None
    description: Optional[str] = None
    cost: Optional[float] = 0.0
    total_cost: Optional[float] = 0.0
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    items: List[ContractItemDTO] = Field(default_factory=list)

    @field_validator("date_signed", "planned_start", "planned_end", mode="before")
    @classmethod
    def parse_date(cls, v) -> Optional[date]:
        if not v:
            return None
        if isinstance(v, (datetime, date)):
            return v.date() if isinstance(v, datetime) else v
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(v).strip(), fmt).date()
            except ValueError:
                continue
        return None

    def calculate_totals(self):
        """Суммирует все позиции спецификации в стоимость договора"""
        summed_items = sum(item.total_price for item in self.items) # type: ignore
        self.cost = summed_items
        self.total_cost = summed_items


class WorkDTO(BaseModel):
    """Конкретная работа (задача)"""
    title: str
    cost: Optional[float] = 0.0
    deadline: Optional[date] = None
    contracts: List[ContractDTO] = Field(default_factory=list)

    @field_validator("cost", mode="before")
    @classmethod
    def clean_cost(cls, v) -> float:
        if v is None:
            return 0.0
        if isinstance(v, (int, float)):
            return float(v)
        cleaned = str(v).replace(" ", "").replace(",", ".").replace("\xa0", "").strip()
        cleaned = "".join(c for c in cleaned if c.isdigit() or c in ".-")
        return float(cleaned) if cleaned else 0.0

    @field_validator("deadline", mode="before")
    @classmethod
    def parse_deadline(cls, v) -> Optional[date]:
        if not v:
            return None
        if isinstance(v, (datetime, date)):
            return v.date() if isinstance(v, datetime) else v
        for fmt in ("%Y-%m-%d", "%d.%m.%Y", "%d/%m/%Y"):
            try:
                return datetime.strptime(str(v).strip(), fmt).date()
            except ValueError:
                continue
        return None


class ObjectDTO(BaseModel):
    """Объект строительства (Строительный адрес)"""
    title: str
    address: Optional[str] = None
    district: Optional[str] = None
    works: List[WorkDTO] = Field(default_factory=list)