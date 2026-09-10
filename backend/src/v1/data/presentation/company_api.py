from typing import List

from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter, Depends, HTTPException, status

from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.data.domain.interfaces import ICompanyUsecases
from backend.src.v1.data.presentation.dtos.data_dto import BaseRequest, BaseResponse
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateRequest, CompanyResponse, CompanyUpdateRequest


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/', response_model=BaseResponse[List[CompanyResponse]])
@inject
async def get_companies(
    uc: FromDishka[ICompanyUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.COMPANY, ActionType.READ))
):
    try:
        result = await uc.get_all_companies()
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings companies")

@router.get('/{company_id}', response_model=BaseResponse[CompanyResponse])
@inject
async def get_company(
    company_id: int,
    uc: FromDishka[ICompanyUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.COMPANY, ActionType.READ))
):
    try:
        result = await uc.get_company_by_id(item_id = company_id)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error gettings company")

@router.post('/', response_model=BaseResponse[CompanyResponse], status_code=status.HTTP_201_CREATED)
@inject
async def create_company(
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyCreateRequest],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.COMPANY, ActionType.CREATE)) 
):
    try:
        result = await uc.create_company(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error creating company")

@router.patch('/{company_id}', response_model=BaseResponse[CompanyResponse])
@inject
async def update_company(
    company_id: int,
    uc: FromDishka[ICompanyUsecases],
    data: BaseRequest[CompanyUpdateRequest],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.COMPANY, ActionType.UPDATE))
):
    try:
        result = await uc.update_company(item_id = company_id, data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error updating company")

@router.delete('/{company_id}', status_code=status.HTTP_204_NO_CONTENT)
@inject
async def delete_company(
    company_id: int,
    uc: FromDishka[ICompanyUsecases],
    current_user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.COMPANY, ActionType.DELETE))
):
    try:
        result = await uc.delete_company(item_id = company_id)
        return
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error deleting company")