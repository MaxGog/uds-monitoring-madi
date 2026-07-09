from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import IWorkUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateRequest, WorkResponse, WorkUpdateRequest

logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[WorkResponse]])
@inject
async def get_works(
    uc: FromDishka[IWorkUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.WORK, ActionType.READ))
):
    try:
        result = await uc.get_works()
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings works")

@router.get('/{work_id}', response_model=BaseResponse[WorkResponse])
@inject
async def get_work(
    work_id: int,
    uc: FromDishka[IWorkUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.WORK, ActionType.READ))
):
    try:
        result = await uc.get_work(item_id = work_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings work")

@router.post('/', response_model=BaseResponse[WorkResponse])
@inject
async def create_work(
    uc: FromDishka[IWorkUsecases],
    data: BaseRequest[WorkCreateRequest], 
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.WORK, ActionType.CREATE))
):
    try:
        result = await uc.create_work(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating work")

@router.patch('/{work_id}', response_model=BaseResponse[WorkResponse])
@inject
async def update_work(
    work_id: int,
    uc: FromDishka[IWorkUsecases],
    data: BaseRequest[WorkUpdateRequest],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.WORK, ActionType.UPDATE))
):
    try:
        result = await uc.update_work(item_id = work_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating work")

@router.delete('/{work_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_work(
    work_id: int,
    uc: FromDishka[IWorkUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.WORK, ActionType.DELETE))
):
    try:
        await uc.delete_work(item_id = work_id)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting work")