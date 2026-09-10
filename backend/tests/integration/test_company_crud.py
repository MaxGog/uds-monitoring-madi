import pytest
from httpx import AsyncClient

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateRequest, CompanyUpdateRequest


@pytest.mark.asyncio(loop_scope = "session")
async def test_company_crud_lifecycle(auth_client: AsyncClient):
    """
    Полный цикл CRUD для компаний.
    Маршруты: /company/
    """
    
    # ==========================================
    # 1. CREATE (POST /company/)
    # ==========================================
    create_dto = CompanyCreateRequest(
        name="Test Corp"
    )
    
    payload = BaseRequest(data=create_dto).model_dump(mode="json", exclude_none=True)
    
    response = await auth_client.post("/company/", json=payload)
    assert response.status_code == 201
    
    created_company = response.json()["data"]
    company_id = created_company["id"]
    assert created_company["name"] == "Test Corp"

    # ==========================================
    # 2. GET ALL (GET /company/)
    # ==========================================
    response = await auth_client.get("/company/")
    assert response.status_code == 200
    
    companies_list = response.json()["data"]
    assert isinstance(companies_list, list)
    assert any(c["id"] == company_id for c in companies_list)

    # ==========================================
    # 3. GET SINGLE (GET /company/{id})
    # ==========================================
    response = await auth_client.get(f"/company/{company_id}")
    assert response.status_code == 200
    
    company_data = response.json()["data"]
    assert company_data["id"] == company_id

    # ==========================================
    # 4. UPDATE (PATCH /company/{id})
    # ==========================================
    update_dto = CompanyUpdateRequest(name="Updated Corp Name")
    
    payload = BaseRequest(data=update_dto).model_dump(mode="json", exclude_unset=True)
    
    response = await auth_client.patch(f"/company/{company_id}", json=payload)
    assert response.status_code == 200
    
    updated_company = response.json()["data"]
    assert updated_company["name"] == "Updated Corp Name"

    # ==========================================
    # 5. DELETE (DELETE /company/{id})
    # ==========================================
    response = await auth_client.delete(f"/company/{company_id}")
    assert response.status_code == 204
    
    # Проверка, что компании больше нет
    get_response = await auth_client.get(f"/company/{company_id}")
    assert get_response.status_code in [404]