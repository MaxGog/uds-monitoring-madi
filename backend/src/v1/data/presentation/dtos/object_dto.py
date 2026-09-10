from typing import Optional

from pydantic import BaseModel, ConfigDict, Field

from backend.src.v1.data.domain.models import ObjectStatus

class CompanyShortResponse(BaseModel):
    id: int
    name: str
    
    model_config = ConfigDict(from_attributes=True)

class ObjectCreateRequest(BaseModel):
    title: str = Field(..., min_length=2, max_length=255, description="Алиас адреса, например 'Большой театр'")
    address: Optional[str] = Field(None, min_length=5, max_length=500)
    district: Optional[str] = Field(None, min_length=2, max_length=100, description="Административный округ")
    supervisor_id: Optional[int] = Field(None, description="ID надзорного органа")
    contractor_id: Optional[int] = Field(None, description="ID подрядчика")
    status: Optional[ObjectStatus] = Field(default=ObjectStatus.PENDING)
    
class ObjectUpdateRequest(BaseModel):
    title: Optional[str] = Field(default=None, min_length=2, max_length=255)
    address: Optional[str] = Field(default=None, min_length=5, max_length=500)
    district: Optional[str] = Field(default=None, min_length=2, max_length=100)
    supervisor_id: Optional[int] = Field(default=None)
    contractor_id: Optional[int] = Field(default=None)
    status: Optional[ObjectStatus] = Field(default=None)

class ObjectResponse(BaseModel):
    id: int
    title: str
    address: Optional[str] = None
    district: Optional[str] = None
    status: Optional[ObjectStatus] = None
    supervisor: Optional[CompanyShortResponse] = None
    contractor: Optional[CompanyShortResponse] = None

    total_completed_cost: Optional[float] = Field(default=None, description="Сумма по всем завершенным актам")

    model_config = ConfigDict(from_attributes=True)