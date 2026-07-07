from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.auth.presentation.api import CurrentUserPayload
from backend.src.v1.data.domain.interfaces import ITaskUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest, TaskCreateResponse, TaskDeleteRequest, TaskDeleteResponse, TaskRequest, TaskResponse, TaskUpdateRequest, TaskUpdateResponse, TasksResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[TasksResponse])
@inject
async def get_tasks(
    current_user: CurrentUserPayload,
    uc: FromDishka[ITaskUsecases],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_tasks(user_id = user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings tasks")

@router.get('/{task_id}', response_model=BaseResponse[TaskResponse])
@inject
async def get_task(
    current_user: CurrentUserPayload,
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskRequest],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_task(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings task")

@router.post('/', response_model=BaseResponse[TaskCreateResponse])
@inject
async def create_task(
    current_user: CurrentUserPayload,
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskCreateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.create_task(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating task")

@router.patch('/{task_id}', response_model=BaseResponse[TaskUpdateResponse])
@inject
async def update_task(
    current_user: CurrentUserPayload,
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskUpdateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.update_task(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating task")

@router.delete('/{task_id}', response_model=BaseResponse[TaskDeleteResponse])
@inject
async def delete_task(
    current_user: CurrentUserPayload,
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskDeleteRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.delete_task(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting task")