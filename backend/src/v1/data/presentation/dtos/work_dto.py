from datetime import date, datetime

from pydantic import BaseModel, Field

# Компактные схемы для вложения в ответ
class ObjectShortResponse(BaseModel):
    id: int
    title: str
    address: str

    class Config:
        from_attributes = True

class ContractorShortResponse(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True

# --- CREATE ---
class WorkCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Наименование работы / тип работы")
    status: str = Field(..., max_length=50, description="Статус работы (например, 'в процессе')")
    cost: float = Field(..., ge=0.0, description="Стоимость работы по смете")
    deadline: date = Field(..., description="Крайний срок выполнения")
    object_id: int = Field(..., description="ID объекта, к которому привязана работа")
    contractor_id: int = Field(..., description="ID подрядчика, выполняющего работу")

# --- UPDATE (PATCH) ---
class WorkUpdateRequest(BaseModel):
    title: str = Field(default=None, min_length=2, max_length=255)
    status: str = Field(default=None, max_length=50)
    cost: float = Field(default=None, ge=0.0)
    deadline: date = Field(default=None)
    object_id: int = Field(default=None)
    contractor_id: int = Field(default=None)

# --- RESPONSE ---
class WorkResponse(BaseModel):
    id: int
    title: str
    status: str
    cost: float
    deadline: date
    created_at: datetime
    updated_at: datetime
    object: ObjectShortResponse
    contractor: ContractorShortResponse

    class Config:
        from_attributes = True