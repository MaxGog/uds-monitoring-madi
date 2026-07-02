from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/')
@inject
async def get_objects(): pass

@router.get('/object')
@inject
async def get_object(): pass

@router.post('create-object')
@inject
async def create_object(): pass

@router.post('delete-object')
@inject
async def delete_object(): pass

@router.post('update-object')
@inject
async def update_object(): pass