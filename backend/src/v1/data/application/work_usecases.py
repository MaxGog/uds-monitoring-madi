from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.work_orm import Work
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IWorkRepo, IWorkUsecases
from backend.src.v1.data.presentation.dtos.work_dto import WorkCreateRequest, WorkResponse, WorkUpdateRequest

logger = logging.getLogger(__name__)

@dataclass
class WorkUsecases(IWorkUsecases):
    uow: IUnitOfWork
    work_repo: IWorkRepo
    user_repo: IUserRepo

    # --- READ (SINGLE) ---
    async def get_work_by_id(self, item_id: int) -> WorkResponse:
        try:
            work = await self.work_repo.get_by_id_with_relations(item_id)
            if not work:
                raise HTTPException(status_code=404, detail="Work record not found")
            return WorkResponse.model_validate(work)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- READ (LIST) ---
    async def get_all_works(self) -> List[WorkResponse]:
        try:    
            works = await self.work_repo.get_all()
            return [WorkResponse.model_validate(w) for w in works]
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # --- CREATE ---
    async def create_work(self, data: WorkCreateRequest) -> WorkResponse:
        logger.info(f"Creating new work estimate: {data.title} for object {data.object_id}")
        try:
            create_data = data.model_dump(exclude_unset = True, exclude_none = True)
            async with self.uow as uow:
                # Валидируем существование связанных сущностей через другие репозитории в UOW
                object_id = create_data.get('object_id')
                if object_id and not await uow.object_repo.get_by_id(object_id):
                    raise HTTPException(status_code=400, detail=f"Object with id {object_id} not found")
                contractor_id = create_data.get('contractor_id')
                if contractor_id and not await uow.company_repo.get_by_id(contractor_id):
                    raise HTTPException(status_code=400, detail=f"Contractor company with id {contractor_id} not found")

                new_work = Work(
                    **create_data
                )
                
                await uow.work_repo.add(new_work)
                await uow.commit()
                
                # Подтягиваем связи для формирования красивого ответа
                work = await uow.work_repo.get_by_id_with_relations(new_work.id)
                return WorkResponse.model_validate(work)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- UPDATE (PATCH) ---
    async def update_work(self, item_id: int, data: WorkUpdateRequest) -> WorkResponse:
        logger.info(f"Patching item_id: {item_id}")
        try:
            async with self.uow as uow:
                work = await uow.work_repo.get_by_id_with_relations(item_id)
                if not work:
                    raise HTTPException(status_code=404, detail="Work record not found")

                update_data = data.model_dump(exclude_unset=True, exclude_none=True)
                if not update_data:
                    return WorkResponse.model_validate(work)

                # Если в PATCH-запросе меняют объект или подрядчика, заново их валидируем
                if "object_id" in update_data:
                    if not await uow.object_repo.get_by_id(update_data["object_id"]):
                        raise HTTPException(status_code=400, detail="Target object not found")
                        
                if "contractor_id" in update_data:
                    if not await uow.company_repo.get_by_id(update_data["contractor_id"]):
                        raise HTTPException(status_code=400, detail="Target contractor company not found")

                # Применяем частичные изменения
                for key, value in update_data.items():
                    setattr(work, key, value)

                await uow.commit()
                
                # Обновляем инстанс в сессии перед отправкой клиенту
                work = await uow.work_repo.get_by_id_with_relations(item_id)
                return WorkResponse.model_validate(work)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- DELETE ---
    async def delete_work(self, item_id: int) -> None:
        logger.info(f"Deleting item_id: {item_id}")
        try:
            async with self.uow as uow:
                work = await uow.work_repo.get_by_id(item_id)
                if not work:
                    raise HTTPException(status_code=404, detail="Work record not found")
                    
                # Здесь при необходимости можно внедрить бизнес-чек: 
                # например, запретить удалять работу, если к ней уже привязаны договоры (self.uow.contract_repo)
                # пока что не будет никаких дополнений
                
                await uow.work_repo.delete(work)
                await uow.commit()
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)