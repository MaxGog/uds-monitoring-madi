from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.object_orm import Object
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IObjectRepo, IObjectUsecases
from backend.src.v1.data.presentation.dtos.object_dto import ObjectCreateRequest, ObjectResponse, ObjectUpdateRequest

logger = logging.getLogger(__file__)

class ObjectUsecases(IObjectUsecases):
    def __init__(self, uow: IUnitOfWork, object_repo: IObjectRepo, user_repo: IUserRepo) -> None:
        self.uow = uow
        self.object_repo = object_repo
        self.user_repo = user_repo

    async def get_objects(self) -> List[ObjectResponse]:
        try:
            objects = await self.object_repo.get_all()   
            result = []
            for obj in objects:
                cost = await self.object_repo.get_total_completed_cost(obj.id)
                dto = ObjectResponse.model_validate(obj)
                dto.total_completed_cost = cost
                result.append(dto)
                
            return result
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    async def get_object_by_id(self, item_id: int) -> ObjectResponse:
        try:
            obj = await self.object_repo.get_by_id_with_relations(item_id)
            if not obj:
                raise HTTPException(status_code=404, detail="Object not found")
                
            cost = await self.object_repo.get_total_completed_cost(obj.id) # Какой то эфемерный метод пока что
            
            response_dto = ObjectResponse.model_validate(obj)
            response_dto.total_completed_cost = cost
            return response_dto
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    async def create_object(self, data: ObjectCreateRequest) -> ObjectResponse:
        logger.info(f"Creating object: {data.title}")
        create_data = data.model_dump(exclude_none=True, exclude_unset=True)
        try:
            async with self.uow as uow:
                supervisor_id = create_data.get("supervisor_id")
                if supervisor_id:
                    if not await uow.company_repo.get_by_id(supervisor_id):
                        raise HTTPException(status_code=400, detail=f"Supervisor company {data.supervisor_id} not found")
                contractor_id = create_data.get("contractor_id")
                if contractor_id:
                    if not await uow.company_repo.get_by_id(contractor_id):
                        raise HTTPException(status_code=400, detail=f"Contractor company {data.contractor_id} not found")

                new_object = Object(
                    **create_data
                )
                await self.uow.object_repo.add(new_object)
                await self.uow.commit()

                obj = await uow.object_repo.get_by_id_with_relations(new_object.id)
                cost = await uow.object_repo.get_total_completed_cost(obj.id) # type: ignore может быть ошибка кнш по рандом багу

                response_dto = ObjectResponse.model_validate(obj)
                return response_dto
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def update_object(self, item_id: int, data: ObjectUpdateRequest) -> ObjectResponse:
        logger.info(f"Patching object_id: {item_id}")
        try:
            async with self.uow as uow:
                obj = await uow.object_repo.get_by_id_with_relations(item_id)
                if not obj:
                    raise HTTPException(status_code=404, detail="Object not found")

                update_data = data.model_dump(exclude_unset=True, exclude_none=True)
                if not update_data:
                    cost = await uow.object_repo.get_total_completed_cost(obj.id)
                    dto = ObjectResponse.model_validate(obj)
                    dto.total_completed_cost = cost
                    return dto

                # Валидация новых ID компаний, если они пришли в запросе
                if "supervisor_id" in update_data:
                    if not await uow.company_repo.get_by_id(update_data["supervisor_id"]):
                        raise HTTPException(status_code=400, detail="New Supervisor company not found")
                if "contractor_id" in update_data:
                    if not await uow.company_repo.get_by_id(update_data["contractor_id"]):
                        raise HTTPException(status_code=400, detail="New Contractor company not found")

                # Применяем PATCH изменения
                for key, value in update_data.items():
                    setattr(obj, key, value)

                await uow.commit()
                
                # Перечитываем и отдаем актуальный стейт
                obj = await uow.object_repo.get_by_id_with_relations(item_id)
                cost = await uow.object_repo.get_total_completed_cost(obj.id) # type: ignore может быть ошибка кнш по рандом багу
                
                dto = ObjectResponse.model_validate(obj)
                dto.total_completed_cost = cost
                return dto
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    async def delete_object(self, item_id: int) -> None:
        logger.info(f"Deleting object_id: {item_id}")
        try:
            async with self.uow as uow:
                obj = await uow.object_repo.get_by_id(item_id)
                if not obj:
                    raise HTTPException(status_code=404, detail="Object not found")
                    
                await uow.object_repo.delete(obj)
                await uow.commit()
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)