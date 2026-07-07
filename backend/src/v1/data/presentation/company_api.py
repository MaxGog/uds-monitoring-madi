from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, HTTPException, status

from backend.src.v1.auth.presentation.api import CurrentUserPayload
from backend.src.v1.data.domain.interfaces import ICompanyUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateRequest, CompanyCreateResponse, CompanyDeleteRequest, CompanyDeleteResponse, CompanyRequest, CompanyResponse, CompanyUpdateRequest, CompanyUpdateResponse, CompanysResponse


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[CompanysResponse])
@inject
async def get_companys(
    current_user: CurrentUserPayload,
    uc: FromDishka[ICompanyUsecases],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_companys(user_id = user_id)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings companys")

@router.get('/{company_id}', response_model=BaseResponse[CompanyResponse])
@inject
async def get_company(
    current_user: CurrentUserPayload,
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyRequest],
):
    user_id = current_user.get('sub')
    try:
        result = await uc.get_company(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings company")

@router.post('/', response_model=BaseResponse[CompanyCreateResponse])
@inject
async def create_company(
    current_user: CurrentUserPayload,
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyCreateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.create_company(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating company")

@router.patch('/{company_id}', response_model=BaseResponse[CompanyUpdateResponse])
@inject
async def update_company(
    current_user: CurrentUserPayload,
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyUpdateRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.update_company(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating company")

@router.delete('/{company_id}', response_model=BaseResponse[CompanyDeleteResponse])
@inject
async def delete_company(
    current_user: CurrentUserPayload,
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyDeleteRequest], 
):
    user_id = current_user.get('sub')
    try:
        result = await uc.delete_company(user_id = user_id, data = data)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting company")