from httpx import AsyncClient
import pytest
from fastapi import status

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateRequest, WorkUpdateRequest
from backend.src.v1.data.domain.models import WorkStatus

@pytest.mark.asyncio(loop_scope = "session")
async def test_work_full_crud_lifecycle(auth_client: AsyncClient):
    # ------------------------------------------------------------------------
    # ШАГ 1: Создание работы (POST)
    # ------------------------------------------------------------------------
    create_payload = WorkCreateRequest(
          title="Облицовка фасада гранитом",
          status = WorkStatus.PENDING,
          cost=850000.00,
          deadline = "2026-11-30",
    )

    
    # Твой роутер возвращает стандартный статус 200 OK на POST (нет 201_CREATED в декораторе)
    payload = BaseRequest(data=create_payload).model_dump(mode="json")
    create_response = await auth_client.post("/work/", json=payload)
    assert create_response.status_code == status.HTTP_200_OK
    
    created_json = create_response.json()
    assert "data" in created_json
    work_id = created_json["data"]["id"]
    assert work_id is not None
    assert created_json["data"]["title"] == "Облицовка фасада гранитом"

    # ------------------------------------------------------------------------
    # ШАГ 2: Проверка наличия в общем списке (GET ALL)
    # ------------------------------------------------------------------------
    list_response = await auth_client.get("/work/")
    assert list_response.status_code == status.HTTP_200_OK
    
    list_json = list_response.json()
    assert len(list_json["data"]) > 0
    # Проверяем, что созданная работа присутствует в массиве
    assert any(item["id"] == work_id for item in list_json["data"])

    # ------------------------------------------------------------------------
    # ШАГ 3: Получение сущности по ID (GET BY ID)
    # ------------------------------------------------------------------------
    get_response = await auth_client.get(f"/work/{work_id}")
    assert get_response.status_code == status.HTTP_200_OK
    
    get_json = get_response.json()
    assert get_json["data"]["id"] == work_id
    assert get_json["data"]["status"] == WorkStatus.PENDING

    # ------------------------------------------------------------------------
    # ШАГ 4: Частичное обновление данных (PATCH)
    # ------------------------------------------------------------------------
    update_payload = WorkUpdateRequest(
        status=WorkStatus.PAUSED,
        cost = 900000.00
    )

    payload = BaseRequest(data = update_payload).model_dump(mode="json")
    update_response = await auth_client.patch(f"/work/{work_id}", json=payload)
    assert update_response.status_code == status.HTTP_200_OK
    
    update_json = update_response.json()
    assert update_json["data"]["status"] == WorkStatus.PAUSED
    assert update_json["data"]["cost"] == 900000.00
    assert update_json["data"]["title"] == "Облицовка фасада гранитом" # Не изменилось

    # ------------------------------------------------------------------------
    # ШАГ 5: Удаление сущности (DELETE)
    # ------------------------------------------------------------------------
    delete_response = await auth_client.delete(f"/work/{work_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.text == ""

    # ------------------------------------------------------------------------
    # ШАГ 6: Проверка удаления (GET после DELETE должен выдать 404)
    # ------------------------------------------------------------------------
    post_delete_response = await auth_client.get(f"/work/{work_id}")
    
    # Так как роутер делает `raise e` для HTTPException, 
    # фейк вернет честный 404 статус код.
    assert post_delete_response.status_code == status.HTTP_404_NOT_FOUND