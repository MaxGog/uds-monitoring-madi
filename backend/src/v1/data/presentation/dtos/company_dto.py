from typing import Optional, List
from pydantic import BaseModel, Field, field_validator

# --- CREATE ---
class CompanyCreateRequest(BaseModel):
    name: str = Field(..., min_length=2, max_length=255, description="Наименование организации")
    inn: Optional[str] = Field(None, pattern=r"^\d{10}$|^\d{12}$", description="ИНН (10 или 12 цифр)")
    kpp: Optional[str] = Field(None, pattern=r"^\d{9}$", description="КПП (9 цифр)")
    address: str = Field(..., min_length=5, max_length=500, description="Юридический/фактический адрес")
    
    # Банковские реквизиты
    bank_account: Optional[str] = Field(None, pattern=r"^\d{20}$", description="Расчетный счет (20 цифр)")
    bank_name: Optional[str] = Field(None, max_length=255, description="Название банка")
    bic: Optional[str] = Field(None, pattern=r"^\d{9}$", description="БИК банка (9 цифр)")

# --- UPDATE (PATCH) ---
class CompanyUpdateRequest(BaseModel):
    name: str = Field(default=None, min_length=2, max_length=255)
    inn: Optional[str] = Field(default=None, pattern=r"^\d{10}$|^\d{12}$")
    kpp: Optional[str] = Field(default=None, pattern=r"^\d{9}$")
    address: str = Field(default=None, min_length=5, max_length=500)
    
    bank_account: Optional[str] = Field(default=None, pattern=r"^\d{20}$")
    bank_name: Optional[str] = Field(default=None, max_length=255)
    bic: Optional[str] = Field(default=None, pattern=r"^\d{9}$")

# --- RESPONSE ---
class CompanyResponse(BaseModel):
    id: int
    name: str
    inn: Optional[str] = None
    kpp: Optional[str] = None
    address: str
    bank_account: Optional[str] = None
    bank_name: Optional[str] = None
    bic: Optional[str] = None

    class Config:
        from_attributes = True