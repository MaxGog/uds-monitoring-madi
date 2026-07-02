from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/')
@inject
async def get_works(): pass

@router.get('/work')
@inject
async def get_work(): pass

@router.post('create-work')
@inject
async def create_work(): pass

@router.post('delete-work')
@inject
async def delete_work(): pass

@router.post('update-work')
@inject
async def update_work(): pass