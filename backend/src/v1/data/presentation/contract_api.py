from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import IContractUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateRequest, ContractResponse, ContractUpdateRequest


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[ContractResponse]])
@inject
async def get_contracts(
    uc: FromDishka[IContractUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.CONTRACT, ActionType.READ))
):
    try:
        result = await uc.get_all_contracts()
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings contracts")

@router.get('/{contract_id}', response_model=BaseResponse[ContractResponse])
@inject
async def get_contract(
    contract_id: int,
    uc: FromDishka[IContractUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.CONTRACT, ActionType.READ))
):
    try:
        result = await uc.get_contract_by_id(item_id = contract_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings contract")

@router.post('/', response_model=BaseResponse[ContractResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_contract(
    data: BaseRequest[ContractCreateRequest],
    uc: FromDishka[IContractUsecases], 
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.CONTRACT, ActionType.CREATE))
):
    try:
        result = await uc.create_contract(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating contract")

@router.patch('/{contract_id}', response_model=BaseResponse[ContractResponse])
@inject
async def update_contract(
    contract_id: int,
    data: BaseRequest[ContractUpdateRequest], 
    uc: FromDishka[IContractUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.CONTRACT, ActionType.UPDATE))
):
    try:
        result = await uc.update_contract(item_id = contract_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating contract")

@router.delete('/{contract_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_contract(
    contract_id: int,
    uc: FromDishka[IContractUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.CONTRACT, ActionType.DELETE))
):
    try:
        await uc.delete_contract(item_id = contract_id)
        return
    except HTTPException as e:
        logger.error(e)
        raise e
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting contract")