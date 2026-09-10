from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, ConfigDict, Field

from backend.src.v1.data.domain.models import ActType, ActStatus


# --- ПОЗИЦИИ АКТА ---
class ActItemBase(BaseModel):
    contract_item_id: int = Field(..., description="ID позиции контракта")
    completed_quantity: float = Field(..., gt=0.0, description="Фактически выполненный объем")

class ActItemResponse(ActItemBase):
    id: int

    model_config = ConfigDict(from_attributes=True)


# --- САМ АКТ ---
class ActCreateRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=50, description="Номер акта")
    status: ActStatus = Field(default=ActStatus.DRAFT)
    date_signed: date = Field(..., description="Дата подписания акта")
    type: Optional[ActType] = Field(default=None, description="Тип акта (госорган / субподряд)")
    metadata_fields: Optional[dict] = Field(default=None, description="Какие либо доп. данные")
    # Внешние ключи (все опциональные по вашей модели)
    object_id: Optional[int] = Field(default=None)
    work_id: Optional[int] = Field(default=None)
    contract_id: Optional[int] = Field(default=None)
    
    # Табличная часть акта
    items: List[ActItemBase] = Field(default_factory=list, description="Позиции акта")

class ActUpdateRequest(BaseModel):
    name: Optional[str] = Field(default=None, min_length=1, max_length=50)
    status: Optional[ActStatus] = Field(default=None)
    date_signed: Optional[date] = Field(default=None)
    type: Optional[ActType] = Field(default=None)
    metadata_fields: Optional[dict] = Field(default=None, description="Какие либо доп. данные")
    object_id: Optional[int] = Field(default=None)
    work_id: Optional[int] = Field(default=None)
    contract_id: Optional[int] = Field(default=None)
    
    # Если прилетит [] — очистим позиции, если None — не трогаем
    items: Optional[List[ActItemBase]] = Field(default=None)

class ActResponse(BaseModel):
    id: int
    name: str
    status: Optional[ActStatus]
    date_signed: Optional[date]
    type: Optional[ActType]
    metadata_fields: Optional[dict] = Field(default=None, description="Какие либо доп. данные")
    object_id: Optional[int]
    work_id: Optional[int]
    contract_id: Optional[int]
    
    items: List[ActItemResponse]

    model_config = ConfigDict(from_attributes=True)