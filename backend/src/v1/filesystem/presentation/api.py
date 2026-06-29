from typing import List

from fastapi import APIRouter
from dishka.integrations.fastapi import FromDishka, inject

router = APIRouter()

@router.get('files')
async def get_files() -> List[str]: 
    
    return []

@router.post('upload')
async def generate_upload_url(
    
):
    pass

@router.get('file_{id}')
async def generate_download_url(): pass