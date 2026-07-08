import logging
from typing import List

from dishka.integrations.fastapi import FromDishka, inject
from fastapi import APIRouter, Depends, HTTPException, Request, Response, status

from backend.src.v1.auth.domain.interfaces import IUserUsecases
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse, UserCreateRequest, UserDeleteRequest, UserRequest, UserResponse, UserUpdateRequest

router = APIRouter()

logger = logging.getLogger(__file__)

# Эндпоинт админа, который создаёт юзеров сам, передавая токены
@router.post("/", response_model=BaseResponse[UserResponse])
@inject
async def create_user(
    current_user: CurrentUserPayload,
    payload: BaseRequest[UserCreateRequest],
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(EntityType.USER, ActionType.CREATE)),
):
    user_id = str(current_user.get('sub'))
    data = payload.data
    try:
        result = await uc.create_user(creator_id = user_id, data = data)
        return {"data": result}
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
    current_user: CurrentUserPayload,
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.READ)),
):
    user_id = str(current_user.get('sub'))
    try:
        result = await uc.get_users(user_id = user_id)
        return { "data": result }
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error getting users")

# TODO реализовать нижестоящие эндпоинты
@router.get('/{user_id}', response_model=BaseResponse[UserResponse])
@inject
async def get_user(
    current_user: CurrentUserPayload,
    data: BaseRequest[UserRequest],
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.READ))
):
    
    pass

@router.patch("/{user_id}", response_model=BaseResponse[UserResponse])
@inject
async def update_user(
    current_user: CurrentUserPayload,
    user_id: str,
    data: BaseRequest[UserUpdateRequest],
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.UPDATE))
):
    request = data.data
    try:
        result = await uc.update_user(user_id, request)
        return BaseResponse(data = result)
    except Exception as e:
        logger.error(e)

@router.delete("/{user_id}", response_model=BaseResponse[UserResponse])
@inject
async def delete_user(
    current_user: CurrentUserPayload,
    data: BaseRequest[UserDeleteRequest],
    uc: FromDishka[IUserUsecases],
    scope: ScopeType = Depends(RequireAccess(entity = EntityType.USER, action = ActionType.DELETE))
    ):
    request = data.data
    #TODO реализовать эндпоинт для удаления пользователя по id, который будет требовать аутентификацию и проверку прав доступа.
    pass