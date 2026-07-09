from pydantic import BaseModel, Field

from backend.src.v1.data.domain.models import ObjectStatus

class CompanyShortResponse(BaseModel):
    id: int
    name: str
    
    class Config:
        from_attributes = True

class ObjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Алиас адреса, например 'Большой театр'")
    address: str = Field(..., min_length=5, max_length=500)
    district: str = Field(..., min_length=2, max_length=100, description="Административный округ")
    supervisor_id: int = Field(..., description="ID надзорного органа")
    contractor_id: int = Field(..., description="ID подрядчика")
    status: ObjectStatus = Field(default=ObjectStatus.PENDING)
    
class ObjectUpdateRequest(BaseModel):
    title: str = Field(default=None, min_length=2, max_length=255)
    address: str = Field(default=None, min_length=5, max_length=500)
    district: str = Field(default=None, min_length=2, max_length=100)
    supervisor_id: int = Field(default=None)
    contractor_id: int = Field(default=None)
    status: ObjectStatus = Field(default=None)

class ObjectResponse(BaseModel):
    id: int
    title: str
    address: str
    district: str
    status: ObjectStatus
    supervisor: CompanyShortResponse
    contractor: CompanyShortResponse
    
    # Безопасно отдаем посчитанную в БД сумму
    total_completed_cost: float = Field(default=0.0, description="Сумма по всем завершенным актам")

    class Config:
        from_attributes = True