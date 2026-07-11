from datetime import date, datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

# Компактные схемы для вложения в ответ
class ObjectShortResponse(BaseModel):
    id: int
    title: str
    address: str

    model_config = ConfigDict(from_attributes=True)

class ContractorShortResponse(BaseModel):
    id: int
    name: str

    model_config = ConfigDict(from_attributes=True)

# --- CREATE ---
class WorkCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Наименование работы / тип работы")
    status: Optional[str] = Field(None, max_length=50, description="Статус работы (например, 'в процессе')")
    cost: Optional[float] = Field(None, ge=0.0, description="Стоимость работы по смете")
    deadline: Optional[date] = Field(None, description="Крайний срок выполнения")
    object_id: Optional[int] = Field(None, description="ID объекта, к которому привязана работа")
    contractor_id: Optional[int] = Field(None, description="ID подрядчика, выполняющего работу")

# --- UPDATE (PATCH) ---
class WorkUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    status: Optional[str] = Field(default=None, max_length=50)
    cost: Optional[float] = Field(default=None, ge=0.0)
    deadline: Optional[date] = Field(default=None)
    object_id: Optional[int] = Field(default=None)
    contractor_id: Optional[int] = Field(default=None)

# --- RESPONSE ---
class WorkResponse(BaseModel):
    id: int
    title: str
    status: Optional[str]
    cost: Optional[float] = None
    deadline: Optional[date] = None
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    object: Optional[ObjectShortResponse] = None
    contractor: Optional[ContractorShortResponse] = None

    model_config = ConfigDict(from_attributes=True)