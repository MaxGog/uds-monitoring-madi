from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.data.domain.interfaces import IActUsecases
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateResponse, ActDeleteResponse, ActResponse, ActUpdateResponse, ActsResponse
from backend.src.v1.data.presentation.dtos.data_dto import BaseResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[ActsResponse])
@inject
async def get_acts(
    uc: FromDishka[IActUsecases],
):
    try:
        result = await uc.get_acts()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings acts")

@router.get('/{act_id}', response_model=BaseResponse[ActResponse])
@inject
async def get_act(
    uc: FromDishka[IActUsecases],
    data: dict,
):
    try:
        result = await uc.get_act(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings act")

@router.post('/', response_model=BaseResponse[ActCreateResponse])
@inject
async def create_act(
    uc: FromDishka[IActUsecases],
    data: dict, 
):
    try:
        result = await uc.create_act(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating act")

@router.patch('/{act_id}', response_model=BaseResponse[ActUpdateResponse])
@inject
async def update_act(
    uc: FromDishka[IActUsecases],
    data: dict, 
):
    try:
        result = await uc.update_act(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating act")

@router.delete('/{act_id}', response_model=BaseResponse[ActDeleteResponse])
@inject
async def delete_act(
    uc: FromDishka[IActUsecases],
    data: dict, 
):
    try:
        result = await uc.delete_act(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting act")