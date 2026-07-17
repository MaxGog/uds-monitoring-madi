from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.act_orm import Act, ActItem
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IActRepo, IActUsecases
from backend.src.v1.data.domain.models import ActStatus
from backend.src.v1.data.presentation.dtos.act_dto import ActCreateRequest, ActResponse, ActUpdateRequest

logger = logging.getLogger(__file__)

class ActUsecases(IActUsecases):
    def __init__(self, uow: IUnitOfWork, act_repo: IActRepo, user_repo: IUserRepo):
        self.uow = uow
        self.act_repo = act_repo
        self.user_repo = user_repo

    # --- READ (SINGLE) ---
    async def get_act_by_id(self, item_id: int) -> ActResponse:
        try:
            act = await self.act_repo.get_by_id_with_relations(item_id)
            if not act:
                raise HTTPException(status_code=404, detail="Work Act not found")
            return ActResponse.model_validate(act)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)

    # --- READ (LIST) ---
    async def get_all_acts(self) -> List[ActResponse]:
        try:
            acts = await self.act_repo.get_all()
            return [ActResponse.model_validate(a) for a in acts]
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- CREATE ---
    async def create_act(self, data: ActCreateRequest) -> ActResponse:
        logger.info(f"Creating work act No: {data.name}")
        try:
            async with self.uow as uow:
                create_data = data.model_dump(exclude_none=True, exclude_unset=True, exclude={'items'})
                # Валидация внешних ключей шапки (если они переданы)
                object_id = create_data.get('object_id')
                if object_id and not await uow.object_repo.get_by_id(object_id):
                    raise HTTPException(status_code=400, detail=f"Object {object_id} not found")
                work_id = create_data.get('object_id')
                if work_id and not await uow.work_repo.get_by_id(work_id):
                    raise HTTPException(status_code=400, detail=f"Work {work_id} not found")
                contract_id = create_data.get('contract_id')
                if contract_id and not await uow.contract_repo.get_by_id(contract_id):
                    raise HTTPException(status_code=400, detail=f"Contract {contract_id} not found")

                requested_item_ids = {item.contract_item_id for item in data.items}

                existing_items = await uow.contract_repo.get_many_by_ids(list(requested_item_ids))
                existing_ids = {item.id for item in existing_items}

                missing_ids = requested_item_ids - existing_ids
                if missing_ids:
                    raise HTTPException(
                        status_code=400, 
                        detail=f"Contract items with IDs {list(missing_ids)} not found"
                    )
                
                orm_items = []
                for item in data.items:
                    orm_items.append(
                        ActItem(
                            contract_item_id=item.contract_item_id,
                            completed_quantity=item.completed_quantity
                        )
                    )

                new_act = Act(
                    **create_data,
                    items=orm_items
                )
                
                await uow.act_repo.add(new_act)
                await uow.commit()
                
                act = await uow.act_repo.get_by_id_with_relations(new_act.id)
                return ActResponse.model_validate(act)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- UPDATE (PATCH) ---
    async def update_act(self, item_id: int, data: ActUpdateRequest) -> ActResponse:
        logger.info(f"Patching work act ID: {item_id}")
        try:
            async with self.uow as uow:
                act = await uow.act_repo.get_by_id_with_relations(item_id)
                if not act:
                    raise HTTPException(status_code=404, detail="Work Act not found")

                update_data = data.model_dump(exclude_unset=True, exclude_none=True)
                if not update_data:
                    return ActResponse.model_validate(act)

                # Валидация при изменении ссылок в шапке
                if "object_id" in update_data and update_data["object_id"]:
                    if not await uow.object_repo.get_by_id(update_data["object_id"]):
                        raise HTTPException(status_code=400, detail="Target object not found")
                if "work_id" in update_data and update_data["work_id"]:
                    if not await uow.work_repo.get_by_id(update_data["work_id"]):
                        raise HTTPException(status_code=400, detail="Target work not found")
                if "contract_id" in update_data and update_data["contract_id"]:
                    if not await uow.contract_repo.get_by_id(update_data["contract_id"]):
                        raise HTTPException(status_code=400, detail="Target contract not found")

                # Обновление табличной части (позиций акта)
                if "items" in update_data:
                    new_items_data = update_data.pop("items")
                    
                    # Полностью очищаем старые позиции (благодаря cascade="all, delete-orphan" они удалятся из БД)
                    act.items.clear()
                    
                    # Наполняем новыми позициями
                    if new_items_data:
                        for item_dto in new_items_data:
                            act.items.append(
                                ActItem(
                                    contract_item_id=item_dto.contract_item_id,
                                    completed_quantity=item_dto.completed_quantity
                                )
                            )

                # Обновление простых полей шапки
                for key, value in update_data.items():
                    setattr(act, key, value)

                await uow.commit()
                
                # Перечитываем актуальный стейт со связями
                act = await uow.act_repo.get_by_id_with_relations(item_id)
                return ActResponse.model_validate(act)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- DELETE ---
    async def delete_act(self, item_id: int) -> None:
        logger.info(f"Deleting work act ID: {item_id}")
        try:
            async with self.uow as uow:
                act = await uow.act_repo.get_by_id(item_id)
                if not act:
                    raise HTTPException(status_code=404, detail="Work Act not found")
                    
                # Бизнес-логика: запрещаем удалять акты в статусе COMPLETED/APPROVED без согласования
                if act.status in [ActStatus.APPROVED, ActStatus.COMPLETED]:
                    raise HTTPException(
                        status_code=400, 
                        detail="Cannot delete an approved or completed work act. Demote its status first."
                    )

                await uow.act_repo.delete(act)
                await uow.commit()
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)