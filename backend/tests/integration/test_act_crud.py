from datetime import date

from fastapi import status
from httpx import AsyncClient
import pytest

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.domain.models import ActStatus, ActType
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateRequest, ActUpdateRequest

@pytest.mark.asyncio(loop_scope='session')
async def test_act_full_crud_lifecycle(auth_client: AsyncClient):
    # ------------------------------------------------------------------------
    # ШАГ 1: Создание акта (POST)
    # ------------------------------------------------------------------------
    create_dto = ActCreateRequest(
          name = "Акт освидетельствования скрытых работ №12",
          status=ActStatus.PENDING,
          type = ActType.CONTRACTOR,
          date_signed=date.today(),
          metadata_fields = {"weather_conditions": "sunny"}
    )
    payload = BaseRequest(data = create_dto).model_dump(mode='json')
    create_response = await auth_client.post("/act/", json=payload)
    assert create_response.status_code == status.HTTP_201_CREATED
    
    created_json = create_response.json()
    assert "data" in created_json
    act_id = created_json["data"]["id"]
    assert act_id is not None
    assert created_json["data"]["name"] == "Акт освидетельствования скрытых работ №12"

    # ------------------------------------------------------------------------
    # ШАГ 2: Проверка наличия в общем списке (GET ALL)
    # ------------------------------------------------------------------------
    list_response = await auth_client.get("/act/")
    assert list_response.status_code == status.HTTP_200_OK
    
    list_json = list_response.json()
    assert len(list_json["data"]) > 0
    # Проверяем, что созданный акт точно есть в списке по его ID
    assert any(item["id"] == act_id for item in list_json["data"])

    # ------------------------------------------------------------------------
    # ШАГ 3: Получение конкретного акта по ID (GET BY ID)
    # ------------------------------------------------------------------------
    get_response = await auth_client.get(f"/act/{act_id}")
    assert get_response.status_code == status.HTTP_200_OK
    
    get_json = get_response.json()
    assert get_json["data"]["id"] == act_id
    assert get_json["data"]["status"] == ActStatus.PENDING
    assert get_json["data"]["metadata_fields"]["weather_conditions"] == "sunny"

    # ------------------------------------------------------------------------
    # ШАГ 4: Частичное обновление через DTO (PATCH)
    # ------------------------------------------------------------------------
    update_dto = ActUpdateRequest(
        name="Акт скрытых работ №12 (Подписан)",
        status=ActStatus.DRAFT,
    )

    payload = BaseRequest(data = update_dto).model_dump(mode='json')
    update_response = await auth_client.patch(f"/act/{act_id}", json=payload)
    assert update_response.status_code == status.HTTP_200_OK
    
    update_json = update_response.json()
    assert update_json["data"]["status"] == ActStatus.DRAFT
    assert update_json["data"]["name"] == "Акт скрытых работ №12 (Подписан)"

    # ------------------------------------------------------------------------
    # ШАГ 5: Удаление акта (DELETE)
    # ------------------------------------------------------------------------
    delete_response = await auth_client.delete(f"/act/{act_id}")
    assert delete_response.status_code == status.HTTP_204_NO_CONTENT
    assert delete_response.text == ""

    # ------------------------------------------------------------------------
    # ШАГ 6: Проверка удаления (GET после DELETE)
    # ------------------------------------------------------------------------
    post_delete_response = await auth_client.get(f"/act/{act_id}")
    
    assert post_delete_response.status_code == status.HTTP_404_NOT_FOUND