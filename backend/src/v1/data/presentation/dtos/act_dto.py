from datetime import date, datetime
from typing import Optional, List
from pydantic import BaseModel, Field

from backend.src.v1.data.domain.models import ActType, WorkActStatus


# --- ПОЗИЦИИ АКТА ---
class WorkActItemBase(BaseModel):
    contract_item_id: int = Field(..., description="ID позиции контракта")
    completed_quantity: float = Field(..., gt=0.0, description="Фактически выполненный объем")

class WorkActItemCreate(WorkActItemBase):
    pass

class WorkActItemResponse(WorkActItemBase):
    id: int

    class Config:
        from_attributes = True


# --- САМ АКТ ---
class WorkActCreateRequest(BaseModel):
    number: str = Field(..., min_length=1, max_length=50, description="Номер акта")
    status: WorkActStatus = Field(default=WorkActStatus.DRAFT)
    date_signed: date = Field(..., description="Дата подписания акта")
    type: Optional[ActType] = Field(default=None, description="Тип акта (госорган / субподряд)")
    
    # Внешние ключи (все опциональные по вашей модели)
    object_id: Optional[int] = Field(default=None)
    work_id: Optional[int] = Field(default=None)
    contract_id: Optional[int] = Field(default=None)
    
    # Табличная часть акта
    items: List[WorkActItemCreate] = Field(default_factory=list, description="Позиции акта")

class WorkActUpdateRequest(BaseModel):
    number: str = Field(default=None, min_length=1, max_length=50)
    status: WorkActStatus = Field(default=None)
    date_signed: date = Field(default=None)
    type: Optional[ActType] = Field(default=None)
    object_id: Optional[int] = Field(default=None)
    work_id: Optional[int] = Field(default=None)
    contract_id: Optional[int] = Field(default=None)
    
    # Если прилетит [] — очистим позиции, если None — не трогаем
    items: Optional[List[WorkActItemCreate]] = Field(default=None)

class WorkActResponse(BaseModel):
    id: int
    number: str
    status: WorkActStatus
    date_signed: date
    type: Optional[ActType]
    object_id: Optional[int]
    work_id: Optional[int]
    contract_id: Optional[int]
    
    items: List[WorkActItemResponse]

    class Config:
        from_attributes = True