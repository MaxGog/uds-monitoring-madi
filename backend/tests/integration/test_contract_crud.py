
from httpx import AsyncClient
import pytest
from fastapi import status

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.domain.models import ContractStatus, ContractType
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateRequest, ContractUpdateRequest


@pytest.mark.asyncio(loop_scope = "session")
async def test_contract_full_crud_lifecycle(auth_client: AsyncClient):
    # ------------------------------------------------------------------------
    # ШАГ 1: Создание контракта (POST)
    # ------------------------------------------------------------------------
    data = ContractCreateRequest(
        contract_id="CNT-2026-X",
        cost=500000.00,
        status=ContractStatus.DRAFT,
        description='Тестовый контракт на разработку'
    ) # type: ignore
    
    payload = BaseRequest(data = data).model_dump(mode="json")
    create_response = await auth_client.post("/contract/", json=payload)
    assert create_response.status_code == status.HTTP_201_CREATED
    
    created_json = create_response.json()
    assert "data" in created_json
    contract_id = created_json["data"]["id"]
    assert contract_id is not None
    assert created_json["data"]["contract_id"] == "CNT-2026-X"

    # ------------------------------------------------------------------------
    # ШАГ 2: Проверка наличия в списке (GET ALL)
    # ------------------------------------------------------------------------
    list_response = await auth_client.get("/contract/")
    assert list_response.status_code == status.HTTP_200_OK
    
    list_json = list_response.json()
    assert len(list_json["data"]) > 0
    # Ищем наш созданный контракт в списке по id
    found_in_list = any(item["id"] == contract_id for item in list_json["data"])
    assert found_in_list is True

    # ------------------------------------------------------------------------
    # ШАГ 3: Получение конкретного контракта по ID (GET BY ID)
    # ------------------------------------------------------------------------
    get_response = await auth_client.get(f"/contract/{contract_id}")
    assert get_response.status_code == status.HTTP_200_OK
    
    get_json = get_response.json()
    assert get_json["data"]["id"] == contract_id
    assert get_json["data"]["status"] == "draft"

    # ------------------------------------------------------------------------
    # ШАГ 4: Обновление данных контракта (PATCH)
    # ------------------------------------------------------------------------
    update_payload = ContractUpdateRequest(
        status=ContractStatus.ACTIVE,
        cost=550000
    )
    payload = BaseRequest(data = update_payload).model_dump(mode = "json")
    update_response = await auth_client.patch(f"/contract/{contract_id}", json=payload)
    assert update_response.status_code == status.HTTP_200_OK
    
    update_json = update_response.json()
    assert update_json["data"]["status"] == "active"
    assert update_json["data"]["cost"] == 550000.00

    # ------------------------------------------------------------------------
    # ШАГ 5: Удаление контракта (DELETE)
    # ------------------------------------------------------------------------
    delete_response = await auth_client.delete(f"/contract/{contract_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.text == ""

    # ------------------------------------------------------------------------
    # ШАГ 6: Проверка удаления (GET после DELETE должен вернуть 404 или ошибку)
    # ------------------------------------------------------------------------
    post_delete_response = await auth_client.get(f"/contract/{contract_id}")
    # В зависимости от логики твоего Usecase здесь может быть либо 404 Not Found, 
    # либо 500 (если падает необработанное исключение)
    assert post_delete_response.status_code in [status.HTTP_404_NOT_FOUND]