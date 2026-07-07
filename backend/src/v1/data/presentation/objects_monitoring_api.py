from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.data.domain.interfaces import IObjectUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseResponse
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateResponse, ObjectDeleteResponse, ObjectResponse, ObjectUpdateResponse, ObjectsResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[ObjectsResponse])
@inject
async def get_objects(
    uc: FromDishka[IObjectUsecases],
):
    try:
        result = await uc.get_objects()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings objects")

@router.get('/{object_id}', response_model=BaseResponse[ObjectResponse])
@inject
async def get_object(
    uc: FromDishka[IObjectUsecases],
    data: dict,
):
    try:
        result = await uc.get_object(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings object")

@router.post('/', response_model=BaseResponse[ObjectCreateResponse])
@inject
async def create_object(
    uc: FromDishka[IObjectUsecases],
    data: dict, 
):
    try:
        result = await uc.create_object(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating object")

@router.patch('/{object_id}', response_model=BaseResponse[ObjectUpdateResponse])
@inject
async def update_object(
    uc: FromDishka[IObjectUsecases],
    data: dict, 
):
    try:
        result = await uc.update_object(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating object")

@router.delete('/{object_id}', response_model=BaseResponse[ObjectDeleteResponse])
@inject
async def delete_object(
    uc: FromDishka[IObjectUsecases],
    data: dict, 
):
    try:
        result = await uc.delete_object(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting object")