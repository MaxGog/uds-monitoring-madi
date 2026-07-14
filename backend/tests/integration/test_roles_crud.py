import uuid

import pytest
from httpx import AsyncClient
from sqlalchemy import select

from backend.core.db.postgres.data_orms.role_orm import Permission, Role, role_permissions
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.dto.role_dto import PermissionCreateRequest, RoleCreateRequest, RoleUpdateRequest
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest

#python -m pytest backend/tests/integration/test_roles_crud.py

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
        permissions=[]
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


@pytest.mark.asyncio(loop_scope="session")
async def test_create_role_with_mixed_permissions(auth_client: AsyncClient, uow):
    """
    Тест создания роли со смешанными правами через API.
    """
    # ------------------------------------------------------------------------
    # ПОДГОТОВКА ДАННЫХ (ARRANGE) через UOW
    # ------------------------------------------------------------------------
    existing_perm_id = None
    dynamic_entity = EntityType.CONTRACT
    dynamic_action = ActionType.MANAGE
    unique_role_name = f"manager_{uuid.uuid4().hex[:6]}"

    async with uow:
        # 1. Используем Get-or-Create логику для существующего пермишена
        existing_perm = await uow.permission_repo.get_by_entity_and_action(
            entity=EntityType.TASK, 
            action=ActionType.READ
        )
        if not existing_perm:
            existing_perm = await uow.permission_repo.create(
                entity=EntityType.TASK, 
                action=ActionType.READ
            )
        
        await uow.commit()
        existing_perm_id = existing_perm.id

        # 2. Гарантируем, что динамического пермишена точно НЕТ в базе (для чистоты теста)
        await uow.permission_repo.delete_by_entity_and_action(
            entity=dynamic_entity, 
            action=dynamic_action
        )
        await uow.commit()

    # ------------------------------------------------------------------------
    # ДЕЙСТВИЕ (ACT) — Запрос к API
    # ------------------------------------------------------------------------
    payload = RoleCreateRequest(
        name=unique_role_name,
        scope=ScopeType.LOCAL,
        permissions=[
            existing_perm_id,
            PermissionCreateRequest(
                action=dynamic_action,
                entity=dynamic_entity,
            )
        ]
    )

    create_payload = BaseRequest(data = payload).model_dump(mode = 'json')
    response = await auth_client.post("/role/", json=create_payload)

    # ------------------------------------------------------------------------
    # ПРОВЕРКА ОТВЕТА (ASSERT)
    # ------------------------------------------------------------------------
    assert response.status_code == 201
    response_data = response.json()["data"]
    role_id = response_data["id"]
    
    assert response_data["name"] == unique_role_name
    assert len(response_data["permissions"]) == 2

    # ------------------------------------------------------------------------
    # ПРОВЕРКА СОСТОЯНИЯ БД (ASSERT) через UOW
    # ------------------------------------------------------------------------
    async with uow:
        db_role = await uow.role_repo.get_by_id(role_id)
        assert db_role is not None
        assert len(db_role.permissions) == 2

        db_perm_pairs = {(p.entity, p.action) for p in db_role.permissions}
        assert (EntityType.TASK, ActionType.READ) in db_perm_pairs
        assert (dynamic_entity, dynamic_action) in db_perm_pairs


@pytest.mark.asyncio(loop_scope="session")
async def test_delete_role_cascades_relations_but_keeps_permissions(auth_client: AsyncClient, uow):
    """
    Тест удаления роли через API.
    """
    # ------------------------------------------------------------------------
    # ПОДГОТОВКА ДАННЫХ (ARRANGE) через UOW
    # ------------------------------------------------------------------------
    role_id = None
    perm_id = None
    role_name = f"test_delete_role_{uuid.uuid4().hex[:6]}"

    async with uow:
        # 1. Тоже используем Get-or-Create для пермишена
        perm = await uow.permission_repo.get_by_entity_and_action(
            entity=EntityType.DOCUMENT, 
            action=ActionType.CREATE
        )
        if not perm:
            perm = await uow.permission_repo.create(
                entity=EntityType.DOCUMENT, 
                action=ActionType.CREATE
            )
        
        await uow.commit()
        perm_id = perm.id

        # 2. Создаем роль и связываем с этим пермишеном
        new_role = Role(name=role_name, scope=ScopeType.LOCAL, permissions=[perm])
        await uow.role_repo.add(new_role)
        await uow.commit()
        role_id = new_role.id

    # ------------------------------------------------------------------------
    # ДЕЙСТВИЕ (ACT) — Удаление роли через API
    # ------------------------------------------------------------------------
    response = await auth_client.delete(f"/role/{role_id}")
    assert response.status_code in (204, 200)

    # ------------------------------------------------------------------------
    # ПРОВЕРКА В БД (ASSERT) через UOW
    # ------------------------------------------------------------------------
    async with uow:
        # 1. Сама роль стерта
        uow.session.expire_all()
        
        deleted_role = await uow.role_repo.get_by_id(role_id)
        assert deleted_role is None

        # 2. Пермишен остался в базе невредим
        existing_perm = await uow.permission_repo.get_by_ids([perm_id])
        assert len(existing_perm) == 1

        # 3. Связующая таблица очищена каскадом
        stmt_m2m = select(role_permissions).where(role_permissions.c.role_id == role_id)
        m2m_links = (await uow.session.execute(stmt_m2m)).all()
        assert len(m2m_links) == 0