import uuid

import pytest
from httpx import AsyncClient

from backend.src.v1.auth.domain.role_models import ScopeType
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleUpdateRequest
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest

@pytest.mark.asyncio(loop_scope="session")
async def test_role_crud_lifecycle(auth_client: AsyncClient):
    """
    Полный цикл (CRUD) тестирования роли:
    Создание -> Получение списка -> Получение одной -> Обновление -> Удаление
    """
    # Генерируем уникальное имя, чтобы тест не падал при повторных запусках
    unique_name = f"Менеджер {uuid.uuid4().hex[:6]}"
    
    # ==========================================
    # 1. CREATE (Создаем роль)
    # ==========================================
    role_data = BaseRequest(data = RoleCreateRequest(
        name=unique_name,
        scope=ScopeType.LOCAL,
        permission_ids=[]
    ))

    create_response = await auth_client.post("/role/", json=role_data.model_dump())
    assert create_response.status_code == 201
    
    created_role = create_response.json()["data"]
    role_id = created_role["id"]
    
    assert created_role["name"] == unique_name

    # ==========================================
    # 2. GET ALL (Проверяем, что она появилась в списке)
    # ==========================================
    get_all_response = await auth_client.get("/role/")
    assert get_all_response.status_code == 200
    
    roles_list = get_all_response.json()["data"]
    assert isinstance(roles_list, list)
    assert role_id in [r["id"] for r in roles_list]

    # ==========================================
    # 3. GET SINGLE (Получаем конкретно её)
    # ==========================================
    get_single_response = await auth_client.get(f"/role/{role_id}")
    assert get_single_response.status_code == 200
    
    role_data = get_single_response.json()["data"]
    assert role_data["id"] == role_id
    assert role_data["name"] == unique_name

    # ==========================================
    # 4. UPDATE (Изменяем имя роли)
    # ==========================================
    new_name = f"Обновленный {unique_name}"
    update_data = BaseRequest(data = RoleUpdateRequest(
        name=new_name,
        scope= ScopeType.LOCAL
    ))
    update_response = await auth_client.patch(f"/role/{role_id}", json=update_data.model_dump())
    assert update_response.status_code == 200
    
    updated_role = update_response.json()["data"]
    assert updated_role["name"] == new_name

    # ==========================================
    # 5. DELETE (Удаляем роль)
    # ==========================================
    delete_response = await auth_client.delete(f"/role/{role_id}")
    assert delete_response.status_code == 204

    # ==========================================
    # 6. VERIFY DELETION (Убеждаемся, что её больше нет)
    # ==========================================
    verify_response = await auth_client.get(f"/role/{role_id}")
    assert verify_response.status_code in [404, 500]
