import logging
from fastapi import APIRouter

from backend.src.v1.auth.presentation.dto.role_dto import RoleCreateResponse, RoleDeleteResponse, RoleResponse, RoleUpdateResponse, RolesResponse
from backend.src.v1.auth.presentation.dto.user_dto import BaseResponse
from fastapi import APIRouter, Request, Response, status
from dishka.integrations.fastapi import FromDishka, inject


router = APIRouter()

logger = logging.getLogger(__file__)

@router.get('/', response_model=BaseResponse[RolesResponse])
@inject
async def get_roles(

):
    pass

@router.get('/{role_id}', response_model=BaseResponse[RoleResponse])
@inject
async def get_role(

):
    pass


@router.post('/', response_model=BaseResponse[RoleCreateResponse])
@inject
async def create_role(

):
    pass

@router.patch('/{role_id}', response_model=BaseResponse[RoleUpdateResponse])
@inject
async def update_role(

):
    pass

@router.delete('/{role_id}', response_model=BaseResponse[RoleDeleteResponse])
async def delete_role(

):
    pass