from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/')
@inject
async def get_acts(): pass

@router.get('/act')
@inject
async def get_act(): pass

@router.post('create-act')
@inject
async def create_act(): pass

@router.post('delete-act')
@inject
async def delete_act(): pass

@router.post('update-act')
@inject
async def update_act(): pass