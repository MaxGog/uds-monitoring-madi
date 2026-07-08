import logging
from typing import List

from fastapi import APIRouter, Depends, HTTPException


from backend.src.v1.auth.domain.interfaces import IRoleUsecases
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateRequest, RoleCreateResponse, RoleResponse, RoleUpdateRequest
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse
from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter()

logger = logging.getLogger(__file__)

@router.get('/', response_model=BaseResponse[List[RoleResponse]])
@inject
async def get_roles(
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.READ))
):
    try:
        result = await uc.get_all_roles()
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.get('/{role_id}', response_model=BaseResponse[RoleResponse])
@inject
async def get_role(
    role_id: int,
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.READ))
):
    try:
        result = await uc.get_role_by_id(role_id)
        return BaseResponse(data=result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


@router.post('/', response_model=BaseResponse[RoleCreateResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_role(
    payload: BaseRequest[RoleCreateRequest],
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.CREATE)),
):
    try:
        result = await uc.create_role(payload.data)
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.patch('/{role_id}', response_model=BaseResponse[RoleResponse])
@inject
async def update_role(
    role_id: int,
    payload: BaseRequest[RoleUpdateRequest],
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.UPDATE))
):
    """
    Частичное обновление роли.
    Передавайте только те поля, которые хотите изменить. 
    Если стереть поле из Swagger — оно проигнорируется.
    """
    try:
        result = await uc.update_role(payload.data)
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.delete('/{role_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_role(
    role_id: int,
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.DELETE))
):
    """Удаление роли по ID (если к ней не привязаны пользователи)"""
    try:
        await uc.delete_role(role_id)
        # Для 204 No Content возвращать BaseResponse не нужно, FastAPI сам отдаст пустой боди
        return
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

@router.post('/test', tags=['dev-tools'], response_model=BaseResponse[RoleCreateResponse])
@inject
async def create_role_dev(
    uc: FromDishka[IRoleUsecases],
    data: BaseRequest[RoleCreateRequest],
):
    try:
        result = await uc.create_role(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)