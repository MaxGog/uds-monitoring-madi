from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/')
@inject
async def get_tasks(): pass

@router.get('/task')
@inject
async def get_task(): pass

@router.post('create-task')
@inject
async def create_task(): pass

@router.post('delete-task')
@inject
async def delete_task(): pass

@router.post('update-task')
@inject
async def update_task(): pass