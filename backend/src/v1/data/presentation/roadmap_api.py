from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.data.domain.interfaces import IRoadmapUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseResponse
from backend.src.v1.data.presentation.dtos.roadmap_dto import RoadmapCreateResponse, RoadmapDeleteResponse, RoadmapResponse, RoadmapUpdateResponse, RoadmapsResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[RoadmapsResponse])
@inject
async def get_roadmaps(
    uc: FromDishka[IRoadmapUsecases],
):
    try:
        result = await uc.get_roadmaps()
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings roadmaps")

@router.get('/{roadmap_id}', response_model=BaseResponse[RoadmapResponse])
@inject
async def get_roadmap(
    uc: FromDishka[IRoadmapUsecases],
    data: dict,
):
    try:
        result = await uc.get_roadmap(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings roadmap")

@router.post('/', response_model=BaseResponse[RoadmapCreateResponse])
@inject
async def create_roadmap(
    uc: FromDishka[IRoadmapUsecases],
    data: dict, 
):
    try:
        result = await uc.create_roadmap(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating roadmap")

@router.patch('/{roadmap_id}', response_model=BaseResponse[RoadmapUpdateResponse])
@inject
async def update_roadmap(
    uc: FromDishka[IRoadmapUsecases],
    data: dict, 
):
    try:
        result = await uc.update_roadmap(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating roadmap")

@router.delete('/{roadmap_id}', response_model=BaseResponse[RoadmapDeleteResponse])
@inject
async def delete_roadmap(
    uc: FromDishka[IRoadmapUsecases],
    data: dict, 
):
    try:
        result = await uc.delete_roadmap(data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting roadmap")