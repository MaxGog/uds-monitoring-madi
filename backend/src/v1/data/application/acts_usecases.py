from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException

from backend.core.db.postgres.data_orms.act_orm import WorkAct, WorkActItem
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IActRepo, IActUsecases
from backend.src.v1.data.domain.models import WorkActStatus
from backend.src.v1.data.presentation.dtos.act_dto import WorkActCreateRequest, WorkActResponse, WorkActUpdateRequest

logger = logging.getLogger(__file__)

class ActUsecases(IActUsecases):
    uow: IUnitOfWork
    act_repo: IActRepo
    user_repo: IUserRepo

    # --- READ (SINGLE) ---
    async def get_act_by_id(self, item_id: int) -> WorkActResponse:
        act = await self.act_repo.get_by_id_with_relations(item_id)
        if not act:
            raise HTTPException(status_code=404, detail="Work Act not found")
        return WorkActResponse.model_validate(act)

    # --- READ (LIST) ---
    async def get_all_acts(self) -> List[WorkActResponse]:
        acts = await self.act_repo.get_all()
        return [WorkActResponse.model_validate(a) for a in acts]

    # --- CREATE ---
    async def create_act(self, data: WorkActCreateRequest) -> WorkActResponse:
        logger.info(f"Creating work act No: {data.number}")
        
        async with self.uow as uow:
            # Валидация внешних ключей шапки (если они переданы)
            if data.object_id and not await uow.object_repo.get_by_id(data.object_id):
                raise HTTPException(status_code=400, detail=f"Object {data.object_id} not found")
            if data.work_id and not await uow.work_repo.get_by_id(data.work_id):
                raise HTTPException(status_code=400, detail=f"Work {data.work_id} not found")
            if data.contract_id and not await uow.contract_repo.get_by_id(data.contract_id):
                raise HTTPException(status_code=400, detail=f"Contract {data.contract_id} not found")

            # Формируем позиции акта
            orm_items = []
            for item in data.items:
                # Здесь можно добавить проверку существования contract_item_id через uow если нужно
                orm_items.append(
                    WorkActItem(
                        contract_item_id=item.contract_item_id,
                        completed_quantity=item.completed_quantity
                    )
                )

            new_act = WorkAct(
                number=data.number,
                status=data.status,
                date_signed=data.date_signed,
                type=data.type,
                object_id=data.object_id,
                work_id=data.work_id,
                contract_id=data.contract_id,
                items=orm_items
            )
            
            await uow.act_repo.add(new_act)
            await uow.commit()
            
            act = await uow.act_repo.get_by_id_with_relations(new_act.id)
            return WorkActResponse.model_validate(act)

    # --- UPDATE (PATCH) ---
    async def update_act(self, item_id: int, data: WorkActUpdateRequest) -> WorkActResponse:
        logger.info(f"Patching work act ID: {item_id}")
        
        async with self.uow as uow:
            act = await uow.act_repo.get_by_id_with_relations(item_id)
            if not act:
                raise HTTPException(status_code=404, detail="Work Act not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return WorkActResponse.model_validate(act)

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
                            WorkActItem(
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
            return WorkActResponse.model_validate(act)

    # --- DELETE ---
    async def delete_act(self, item_id: int) -> None:
        logger.info(f"Deleting work act ID: {item_id}")
        async with self.uow as uow:
            act = await uow.act_repo.get_by_id(item_id)
            if not act:
                raise HTTPException(status_code=404, detail="Work Act not found")
                
            # Бизнес-логика: запрещаем удалять акты в статусе COMPLETED/APPROVED без согласования
            if act.status in [WorkActStatus.APPROVED, WorkActStatus.COMPLETED]:
                raise HTTPException(
                    status_code=400, 
                    detail="Cannot delete an approved or completed work act. Demote its status first."
                )

            await uow.act_repo.delete(act)
            await uow.commit()