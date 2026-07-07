from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.auth.presentation.api import CurrentUserPayload
from backend.src.v1.data.domain.interfaces import IContractUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateRequest, ContractCreateResponse, ContractDeleteRequest, ContractDeleteResponse, ContractRequest, ContractResponse, ContractUpdateRequest, ContractUpdateResponse, ContractsResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[ContractsResponse])
@inject
async def get_contracts(
    current_user: CurrentUserPayload,
    uc: FromDishka[IContractUsecases],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_contracts(user_id = user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings contracts")

@router.get('/{contract_id}', response_model=BaseResponse[ContractResponse])
@inject
async def get_contract(
    current_user: CurrentUserPayload,
    uc: FromDishka[IContractUsecases],
    data: BaseRequest[ContractRequest],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_contract(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings contract")

@router.post('/', response_model=BaseResponse[ContractCreateResponse])
@inject
async def create_contract(
    current_user: CurrentUserPayload,
    uc: FromDishka[IContractUsecases],
    data: BaseRequest[ContractCreateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.create_contract(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating contract")

@router.patch('/{contract_id}', response_model=BaseResponse[ContractUpdateResponse])
@inject
async def update_contract(
    current_user: CurrentUserPayload,
    uc: FromDishka[IContractUsecases],
    data: BaseRequest[ContractUpdateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.update_contract(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating contract")

@router.delete('/{contract_id}', response_model=BaseResponse[ContractDeleteResponse])
@inject
async def delete_contract(
    current_user: CurrentUserPayload,
    uc: FromDishka[IContractUsecases],
    data: BaseRequest[ContractDeleteRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.delete_contract(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting contract")