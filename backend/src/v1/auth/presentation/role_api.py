import logging

from fastapi import APIRouter, Depends, HTTPException


from backend.src.v1.auth.domain.interfaces import IRoleUsecases
from backend.src.v1.auth.domain.role_models import ActionType, EntityType, ScopeType
from backend.src.v1.auth.presentation.api import CurrentUserPayload, RequireAccess
from backend.src.v1.auth.presentation.dto.role_dto import PermissionCreate, RoleCreateRequest, RoleCreateResponse, RoleDeleteResponse, RoleResponse, RoleUpdateResponse, RolesResponse
from backend.src.v1.auth.presentation.dto.user_dto import BaseRequest, BaseResponse
from fastapi import APIRouter, status
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter()

logger = logging.getLogger(__file__)

@router.get('/', response_model=BaseResponse[RolesResponse])
@inject
async def get_roles(
    uc: FromDishka[IRoleUsecases],
):
    pass

@router.get('/{role_id}', response_model=BaseResponse[RoleResponse])
@inject
async def get_role(
    uc: FromDishka[IRoleUsecases],
):
    pass


@router.post('/', response_model=BaseResponse[RoleCreateResponse])
@inject
async def create_role(
    payload: BaseRequest[RoleCreateRequest],
    uc: FromDishka[IRoleUsecases],
    user: CurrentUserPayload,
    scope: ScopeType = Depends(RequireAccess(EntityType.ROLE, ActionType.CREATE)),
):
    data = payload.data
    result = await uc.create_role(data)
    return BaseResponse(data=result)

@router.patch('/{role_id}', response_model=BaseResponse[RoleUpdateResponse])
@inject
async def update_role(
    uc: FromDishka[IRoleUsecases],
):
    pass

@router.delete('/{role_id}', response_model=BaseResponse[RoleDeleteResponse])
@inject
async def delete_role(
    uc: FromDishka[IRoleUsecases],
):
    pass

@router.post('/test', tags=['dev-tools'], response_model=BaseResponse[RoleCreateResponse])
@inject
async def create_role_dev(
    uc: FromDishka[IRoleUsecases],
    data: BaseRequest[RoleCreateRequest],
):
    try:
        result = await uc.create_role(data = data.data)
        return BaseResponse(data = result)
    except HTTPException as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        logger.error(e)
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)