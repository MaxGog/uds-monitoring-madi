import pytest
from httpx import AsyncClient

from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateRequest, ObjectUpdateRequest

@pytest.mark.asyncio(loop_scope="session")
async def test_object_crud_lifecycle(auth_client: AsyncClient):
    """
    Полный цикл CRUD для объектов.
    """
    
    # ==========================================
    # 1. CREATE (POST /object/)
    # ==========================================
    create_dto = ObjectCreateRequest(
        title="Test Object"
    )
    
    payload = BaseRequest(data=create_dto).model_dump(mode="json")
    
    response = await auth_client.post("/object/", json=payload)
    assert response.status_code == 201
    
    created_obj = response.json()["data"]
    object_id = created_obj["id"]
    assert created_obj["title"] == "Test Object"

    # ==========================================
    # 2. GET ALL (GET /object/)
    # ==========================================
    response = await auth_client.get("/object/")
    assert response.status_code == 200
    
    objects_list = response.json()["data"]
    assert isinstance(objects_list, list)
    assert any(o["id"] == object_id for o in objects_list)

    # ==========================================
    # 3. GET SINGLE (GET /object/{id})
    # ==========================================
    response = await auth_client.get(f"/object/{object_id}")
    assert response.status_code == 200
    
    obj_data = response.json()["data"]
    assert obj_data["id"] == object_id

    # ==========================================
    # 4. UPDATE (PATCH /object/{id})
    # ==========================================
    update_dto = ObjectUpdateRequest(title="Updated Object Name")
    
    payload = BaseRequest(data=update_dto).model_dump(mode="json", exclude_unset=True)
    
    response = await auth_client.patch(f"/object/{object_id}", json=payload)
    assert response.status_code == 200
    
    updated_obj = response.json()["data"]
    assert updated_obj["title"] == "Updated Object Name"

    # ==========================================
    # 5. DELETE (DELETE /object/{id})
    # ==========================================
    response = await auth_client.delete(f"/object/{object_id}")
    assert response.status_code == 204

    get_response = await auth_client.get(f"/object/{object_id}")
    assert get_response.status_code == 404