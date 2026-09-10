from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import ITaskUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest,TaskResponse, TaskUpdateRequest


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[TaskResponse]])
@inject
async def get_tasks(
    uc: FromDishka[ITaskUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.TASK, ActionType.READ))
):
    try:
        result = await uc.get_tasks()
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings tasks")

@router.get('/{task_id}', response_model=BaseResponse[TaskResponse])
@inject
async def get_task(
    uc: FromDishka[ITaskUsecases],
    task_id: int,
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.TASK, ActionType.READ))
):
    try:
        result = await uc.get_task_by_id(item_id = task_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings task")

@router.post('/', response_model=BaseResponse[TaskResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_task(
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskCreateRequest], 
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.TASK, ActionType.CREATE))
):
    author_id = current_user.get('sub')
    try:
        result = await uc.create_task(author_id = author_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating task")

@router.patch('/{task_id}', response_model=BaseResponse[TaskResponse])
@inject
async def update_task(
    uc: FromDishka[ITaskUsecases],
    task_id: int,
    data: BaseRequest[TaskUpdateRequest], 
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.TASK, ActionType.UPDATE))
):
    try:
        result = await uc.update_task(item_id = task_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating task")

@router.delete('/{task_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_task(
    uc: FromDishka[ITaskUsecases],
    task_id: int,
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.TASK, ActionType.DELETE))
):
    try:
        await uc.delete_task(item_id = task_id)
        return
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting task")