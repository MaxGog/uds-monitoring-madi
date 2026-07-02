from dishka.integrations.fastapi import FromDishka, inject

import logging

from fastapi import APIRouter


logger = logging.getLogger(__file__)

router = APIRouter()

@router.get('/')
@inject
async def get_roadmaps(): pass

@router.get('/roadmap')
@inject
async def get_roadmap(): pass

@router.post('create-roadmap')
@inject
async def create_roadmap(): pass

@router.post('delete-roadmap')
@inject
async def delete_roadmap(): pass

@router.post('update-roadmap')
@inject
async def update_roadmap(): pass