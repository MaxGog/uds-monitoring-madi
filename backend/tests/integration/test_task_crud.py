import pytest
from httpx import AsyncClient

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest, TaskUpdateRequest

@pytest.mark.asyncio(loop_scope="session")
async def test_task_crud_lifecycle(auth_client: AsyncClient):
    """
    Полный цикл CRUD для задач.
    Маршруты: /task/
    """
    
    # ==========================================
    # 1. CREATE (POST /task/)
    # ==========================================
    create_dto = TaskCreateRequest(
        title="Тестовая задача",
        description="Описание задачи для теста"
    )
    
    # Сериализуем с exclude_none=True, чтобы не слать лишние None
    payload = BaseRequest(data=create_dto).model_dump(mode="json")
    
    response = await auth_client.post("/task/", json=payload)
    assert response.status_code == 201
    
    created_task = response.json()["data"]
    task_id = created_task["id"]
    assert created_task["title"] == "Тестовая задача"

    # ==========================================
    # 2. GET ALL (GET /task/)
    # ==========================================
    response = await auth_client.get("/task/")
    assert response.status_code == 200
    
    tasks_list = response.json()["data"]
    assert isinstance(tasks_list, list)
    # Проверяем, что наша задача есть в списке
    assert any(t["id"] == task_id for t in tasks_list)

    # ==========================================
    # 3. GET SINGLE (GET /task/{id})
    # ==========================================
    response = await auth_client.get(f"/task/{task_id}")
    assert response.status_code == 200
    
    task_data = response.json()["data"]
    assert task_data["id"] == task_id

    # ==========================================
    # 4. UPDATE (PATCH /task/{id})
    # ==========================================
    # Используем exclude_unset=True, чтобы слать только измененные поля
    update_dto = TaskUpdateRequest(title="Обновленный заголовок")
    
    payload = BaseRequest(data=update_dto).model_dump(mode="json")
    
    response = await auth_client.patch(f"/task/{task_id}", json=payload)
    assert response.status_code == 200
    
    updated_task = response.json()["data"]
    assert updated_task["title"] == "Обновленный заголовок"
    # Описание должно остаться прежним (если мы его не меняли)
    assert updated_task["description"] == "Описание задачи для теста"

    # ==========================================
    # 5. DELETE (DELETE /task/{id})
    # ==========================================
    response = await auth_client.delete(f"/task/{task_id}")
    assert response.status_code == 204
    
    # Проверка, что задачи больше нет (обычно 404)
    get_response = await auth_client.get(f"/task/{task_id}")
    assert get_response.status_code in [404]