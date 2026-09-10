from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import IObjectUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateRequest, ObjectResponse, ObjectUpdateRequest


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[ObjectResponse]])
@inject
async def get_objects(
    uc: FromDishka[IObjectUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.OBJECT, ActionType.READ))
):
    try:
        result = await uc.get_objects()
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings objects")

@router.get('/{object_id}', response_model=BaseResponse[ObjectResponse])
@inject
async def get_object(
    object_id: int,
    uc: FromDishka[IObjectUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.OBJECT, ActionType.READ))
):
    try:
        result = await uc.get_object_by_id(item_id = object_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings object")

@router.post('/', response_model=BaseResponse[ObjectResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_object(
    uc: FromDishka[IObjectUsecases],
    data: BaseRequest[ObjectCreateRequest],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.OBJECT, ActionType.CREATE)) 
):
    try:
        result = await uc.create_object(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating object")

@router.patch('/{object_id}', response_model=BaseResponse[ObjectResponse])
@inject
async def update_object(
    object_id: int,
    uc: FromDishka[IObjectUsecases],
    data: BaseRequest[ObjectUpdateRequest], 
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.OBJECT, ActionType.UPDATE))
):
    try:
        result = await uc.update_object(item_id = object_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating object")

@router.delete('/{object_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_object(
    object_id: int,
    uc: FromDishka[IObjectUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.OBJECT, ActionType.DELETE))
):
    try:
        result = await uc.delete_object(item_id = object_id)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting object")