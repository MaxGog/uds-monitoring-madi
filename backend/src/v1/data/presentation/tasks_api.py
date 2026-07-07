from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.data.domain.interfaces import ITaskUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.task_dto import TaskCreateRequest, TaskCreateResponse, TaskDeleteRequest, TaskDeleteResponse, TaskRequest, TaskResponse, TaskUpdateRequest, TaskUpdateResponse, TasksResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[TasksResponse])
@inject
async def get_tasks(
    uc: FromDishka[ITaskUsecases],
):
    try:
        result = await uc.get_tasks()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings tasks")

@router.get('/{task_id}', response_model=BaseResponse[TaskResponse])
@inject
async def get_task(
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskRequest],
):
    try:
        result = await uc.get_task(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings task")

@router.post('/', response_model=BaseResponse[TaskCreateResponse])
@inject
async def create_task(
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskCreateRequest], 
):
    try:
        result = await uc.create_task(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating task")

@router.patch('/{task_id}', response_model=BaseResponse[TaskUpdateResponse])
@inject
async def update_task(
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskUpdateRequest], 
):
    try:
        result = await uc.update_task(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating task")

@router.delete('/{task_id}', response_model=BaseResponse[TaskDeleteResponse])
@inject
async def delete_task(
    uc: FromDishka[ITaskUsecases],
    data: BaseRequest[TaskDeleteRequest], 
):
    try:
        result = await uc.delete_task(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting task")