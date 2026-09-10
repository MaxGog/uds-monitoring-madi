from datetime import date
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from backend.src.v1.data.domain.models import ContractStatus, ContractType

# --- ПОЗИЦИИ ДОГОВОРА (СПЕЦИФИКАЦИЯ) ---
class ContractItemCreate(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Наименование работы/обязательства")
    description: Optional[str] = Field(None, description="Описание позиции")
    quantity: float = Field(..., gt=0.0, description="Количество/Объем")
    unit: str = Field(..., min_length=1, max_length=20, description="Ед. изм. (шт, м2, пог.м)")
    price_per_unit: float = Field(..., ge=0.0, description="Цена за единицу")

class ContractItemResponse(BaseModel):
    id: int
    title: str
    description: Optional[str] = None
    quantity: float
    unit: str
    price_per_unit: float
    total_price: float

    model_config = ConfigDict(from_attributes=True)


# --- САМ ДОГОВОР ---
class ContractCreateRequest(BaseModel):
    contract_id: Optional[str] = Field(None, description="Номер договора (например, '№ 45-Б')")
    date_signed: Optional[date] = Field(None, description="Дата подписания")
    description: Optional[str] = Field(None)
    status: Optional[ContractStatus] = Field(default=ContractStatus.DRAFT)
    type: Optional[ContractType] = Field(default=ContractType.GENERAL)
    
    cost: Optional[float] = Field(None, description="Стоимость")
    
    planned_start: Optional[date] = Field(None)
    planned_end: Optional[date] = Field(None)
    actual_start: Optional[date] = Field(None)
    actual_end: Optional[date] = Field(None)
    
    object_id: Optional[int] = Field(None, description="ID связанного объекта")
    work_id: Optional[int] = Field(None, description="ID связанной работы")
    
    items: List[ContractItemCreate] = Field(default_factory=list, description="Спецификация договора")

class ContractUpdateRequest(BaseModel):
    contract_id: Optional[str] = Field(default=None)
    date_signed: Optional[date] = Field(default=None)
    description: Optional[str] = Field(default=None)
    status: Optional[ContractStatus] = Field(default=None)
    type: Optional[ContractType] = Field(default=None)
    
    cost: Optional[float] = Field(default=None)
    
    planned_start: Optional[date] = Field(default=None)
    planned_end: Optional[date] = Field(default=None)
    actual_start: Optional[date] = Field(default=None)
    actual_end: Optional[date] = Field(default=None)
    
    object_id: Optional[int] = Field(default=None)
    work_id: Optional[int] = Field(default=None)
    
    items: Optional[List[ContractItemCreate]] = Field(default=None, description="Полная перезапись спецификации")

class ContractResponse(BaseModel):
    id: int
    contract_id: Optional[str]
    date_signed: Optional[date] = None
    description: Optional[str] = None
    status: Optional[ContractStatus] = None
    type: Optional[ContractType] = None
    cost: Optional[float] = None
    total_cost: Optional[float] = None
    
    planned_start: Optional[date] = None
    planned_end: Optional[date] = None
    actual_start: Optional[date] = None
    actual_end: Optional[date] = None
    
    object_id: Optional[int] = None
    work_id: Optional[int] = None
    
    items: Optional[List[ContractItemResponse]] = []

    model_config = ConfigDict(from_attributes=True)