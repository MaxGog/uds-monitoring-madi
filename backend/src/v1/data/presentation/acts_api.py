from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import IActUsecases
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateRequest, ActResponse, ActUpdateRequest
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[ActResponse]])
@inject
async def get_acts(
    uc: FromDishka[IActUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ACT, ActionType.READ))
):
    try:
        result = await uc.get_all_acts()
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings acts")

@router.get('/{act_id}', response_model=BaseResponse[ActResponse])
@inject
async def get_act(
    act_id: int,
    uc: FromDishka[IActUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ACT, ActionType.READ))
):
    try:
        result = await uc.get_act_by_id(item_id = act_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings act")

@router.post('/', response_model=BaseResponse[ActResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_act(
    uc: FromDishka[IActUsecases],
    data: BaseRequest[ActCreateRequest],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ACT, ActionType.CREATE))
):
    try:
        result = await uc.create_act(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating act")

@router.patch('/{act_id}', response_model=BaseResponse[ActResponse])
@inject
async def update_act(
    act_id: int,
    data: BaseRequest[ActUpdateRequest],
    uc: FromDishka[IActUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ACT, ActionType.UPDATE))
):
    try:
        result = await uc.update_act(item_id = act_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating act")

@router.delete('/{act_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_act(
    act_id: int,
    uc: FromDishka[IActUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ACT, ActionType.DELETE))
):
    try:
        await uc.delete_act(item_id = act_id)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting act")