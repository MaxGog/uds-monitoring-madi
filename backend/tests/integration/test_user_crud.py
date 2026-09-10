import pytest
import uuid
from httpx import AsyncClient

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, UserCreateRequest, UserUpdateRequest

@pytest.mark.asyncio(loop_scope="session")
async def test_user_crud_lifecycle(auth_client: AsyncClient):
    """
    Полный цикл CRUD для пользователя с использованием DTO.
    Маршрут: /user (без 's' на конце)
    """
    unique_id = uuid.uuid4().hex[:8]
    email = f"test_{unique_id}@madi.ru"
    username = f"User_{unique_id}"

    # ==========================================
    # 1. CREATE (POST /user)
    # ==========================================
    create_dto = UserCreateRequest(
        username=username,
        email=email,
        password="SecurePassword123!",
        role_id=None,
        company_id=None,
        full_name=None,
        position=None,
    )
    
    # Оборачиваем в BaseRequest и сериализуем в JSON через mode='json'
    payload = BaseRequest(data=create_dto).model_dump(mode="json")
    
    response = await auth_client.post("/users/", json=payload)
    assert response.status_code == 201
    
    created_user = response.json()["data"]
    user_id = created_user["id"]
    assert created_user["username"] == username

    # ==========================================
    # 2. GET ALL (GET /user)
    # ==========================================
    response = await auth_client.get("/users/")
    assert response.status_code == 200
    
    users_list = response.json()["data"]
    assert isinstance(users_list, list)
    assert any(u["id"] == user_id for u in users_list)

    # ==========================================
    # 3. GET SINGLE (GET /user/{id})
    # ==========================================
    response = await auth_client.get(f"/users/{user_id}")
    assert response.status_code == 200
    
    user_data = response.json()["data"]
    assert user_data["id"] == user_id
    assert user_data["email"] == email

    # ==========================================
    # 4. UPDATE (PATCH /user/{id})
    # ==========================================
    new_username = f"Updated_{unique_id}"
    update_dto = UserUpdateRequest(username=new_username)
    
    payload = BaseRequest(data=update_dto).model_dump(mode="json")
    
    response = await auth_client.patch(f"/users/{user_id}", json=payload)
    assert response.status_code == 200
    
    updated_user = response.json()["data"]
    assert updated_user["username"] == new_username

    # ==========================================
    # 5. DELETE (DELETE /user/{id})
    # ==========================================
    response = await auth_client.delete(f"/users/{user_id}")
    assert response.status_code == 204
    
    # Проверка, что пользователя больше нет
    get_response = await auth_client.get(f"/users/{user_id}")

    assert get_response.status_code in [404, 500]