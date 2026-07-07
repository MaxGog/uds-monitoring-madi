from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.data.domain.interfaces import IWorkUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseResponse
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateResponse, WorkDeleteResponse, WorkResponse, WorkUpdateResponse, WorksResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[WorksResponse])
@inject
async def get_works(
    uc: FromDishka[IWorkUsecases],
):
    try:
        result = await uc.get_works()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings works")

@router.get('/{work_id}', response_model=BaseResponse[WorkResponse])
@inject
async def get_work(
    uc: FromDishka[IWorkUsecases],
    data: dict,
):
    try:
        result = await uc.get_work(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings work")

@router.post('/', response_model=BaseResponse[WorkCreateResponse])
@inject
async def create_work(
    uc: FromDishka[IWorkUsecases],
    data: dict, 
):
    try:
        result = await uc.create_work(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating work")

@router.patch('/{work_id}', response_model=BaseResponse[WorkUpdateResponse])
@inject
async def update_work(
    uc: FromDishka[IWorkUsecases],
    data: dict, 
):
    try:
        result = await uc.update_work(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating work")

@router.delete('/{work_id}', response_model=BaseResponse[WorkDeleteResponse])
@inject
async def delete_work(
    uc: FromDishka[IWorkUsecases],
    data: dict, 
):
    try:
        result = await uc.delete_work(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting work")