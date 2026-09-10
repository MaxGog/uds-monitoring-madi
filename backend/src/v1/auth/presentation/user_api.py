import logging
from typing import List
from uuid import UUID

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from backend.src.v1.auth.domain.interfaces import IUserUsecases
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse, UserCreateRequest, UserResponse, UserUpdateRequest

router = APIRouter()

logger = logging.getLogger(__file__)

# Эндпоинт админа, который создаёт юзеров сам
@router.post("/", response_model=BaseResponse[UserResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_user(
    current_user: CurrentUserPayload,
    data: BaseRequest[UserCreateRequest],
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(EntityType.USER, ActionType.CREATE)),
):
    try:
        result = await uc.create_user(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Couldn't create new user")


@router.get("/me", response_model=BaseResponse[UserResponse])
@inject
async def get_current_user_profile(
    current_user: CurrentUserPayload,
    uc: FromDishka[IUserUsecases],
):
    user_id = str(current_user.get('sub'))
    try:
        result = await uc.get_me(user_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="User not found")
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get('/', response_model=BaseResponse[List[UserResponse]])
@inject
async def get_users(
    uc: FromDishka[IUserUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.READ)),
):
    try:
        result = await uc.get_all_users()
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting users")

@router.get('/{user_id}', response_model=BaseResponse[UserResponse])
@inject
async def get_user(
    user_id: UUID,
    uc: FromDishka[IUserUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.READ))
):
    try:
        result = await uc.get_user_by_id(user_id = user_id)
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting user")

@router.patch("/{user_id}", response_model=BaseResponse[UserResponse])
@inject
async def update_user(
    user_id: UUID,
    data: BaseRequest[UserUpdateRequest],
    uc: FromDishka[IUserUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.UPDATE))
):
    try:
        result = await uc.update_user(user_id, data.data)
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating user")
    
@router.delete("/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_user(
    user_id: UUID,
    uc: FromDishka[IUserUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.DELETE))
):
    try:
        await uc.delete_user(user_id)
        return
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting user")