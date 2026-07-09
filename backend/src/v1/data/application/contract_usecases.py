import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.contract_orm import Contract, ContractItem
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import IContractRepo, IContractUsecases
from backend.src.v1.data.presentation.dtos.contract_dto import ContractCreateRequest, ContractResponse, ContractUpdateRequest

logger = logging.getLogger(__name__)

class ContractUsecases(IContractUsecases):
    uow: IUnitOfWork
    contract_repo: IContractRepo
    user_repo: IUserRepo

    # --- READ (SINGLE) ---
    async def get_contract_by_id(self, item_id: int) -> ContractResponse:
        contract = await self.contract_repo.get_by_id_with_relations(item_id)
        if not contract:
            raise HTTPException(status_code=404, detail="Contract not found")
        return ContractResponse.model_validate(contract)

    # --- READ (LIST) ---
    async def get_all_contracts(self) -> List[ContractResponse]:
        contracts = await self.contract_repo.get_all()
        return [ContractResponse.model_validate(c) for c in contracts]

    # --- CREATE ---
    async def create_contract(self, data: ContractCreateRequest) -> ContractResponse:
        logger.info(f"Creating contract: {data.contract_id}")
        
        async with self.uow as uow:
            # Проверка внешних ключей
            if data.object_id and not await uow.object_repo.get_by_id(data.object_id):
                raise HTTPException(status_code=400, detail=f"Object {data.object_id} not found")
            if data.work_id and not await uow.work_repo.get_by_id(data.work_id):
                raise HTTPException(status_code=400, detail=f"Work {data.work_id} not found")

            # Формируем спецификацию и высчитываем финансовые итоги
            orm_items = []
            calculated_total_cost = 0.0
            
            for item in data.items:
                item_total = round(item.quantity * item.price_per_unit, 2)
                calculated_total_cost += item_total
                
                orm_items.append(
                    ContractItem(
                        title=item.title,
                        description=item.description,
                        quantity=item.quantity,
                        unit=item.unit,
                        price_per_unit=item.price_per_unit,
                        total_price=item_total
                    )
                )

            new_contract = Contract(
                contract_id=data.contract_id,
                date_signed=data.date_signed,
                description=data.description,
                status=data.status,
                type=data.type,
                cost=data.cost,
                total_cost=calculated_total_cost if orm_items else 0.0,
                planned_start=data.planned_start,
                planned_end=data.planned_end,
                actual_start=data.actual_start,
                actual_end=data.actual_end,
                object_id=data.object_id,
                work_id=data.work_id,
                items=orm_items
            )

            await uow.contract_repo.add(new_contract)
            await uow.commit()
            
            contract = await uow.contract_repo.get_by_id_with_relations(new_contract.id)
            return ContractResponse.model_validate(contract)

    # --- UPDATE (PATCH) ---
    async def update_contract(self, item_id: int, data: ContractUpdateRequest) -> ContractResponse:
        logger.info(f"Patching contract ID: {item_id}")
        
        async with self.uow as uow:
            contract = await uow.contract_repo.get_by_id_with_relations(item_id)
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return ContractResponse.model_validate(contract)

            # Валидация связей при их апдейте
            if "object_id" in update_data and update_data["object_id"]:
                if not await uow.object_repo.get_by_id(update_data["object_id"]):
                    raise HTTPException(status_code=400, detail="Target object not found")
            if "work_id" in update_data and update_data["work_id"]:
                if not await uow.work_repo.get_by_id(update_data["work_id"]):
                    raise HTTPException(status_code=400, detail="Target work not found")

            # Перезапись спецификации (табличной части)
            if "items" in update_data:
                new_items_data = update_data.pop("items")
                contract.items.clear()  # Каскадно удаляет старые позиции из базы
                
                calculated_total_cost = 0.0
                if new_items_data:
                    for item_dto in new_items_data:
                        item_total = round(item_dto.quantity * item_dto.price_per_unit, 2)
                        calculated_total_cost += item_total
                        
                        contract.items.append(
                            ContractItem(
                                title=item_dto.title,
                                description=item_dto.description,
                                quantity=item_dto.quantity,
                                unit=item_dto.unit,
                                price_per_unit=item_dto.price_per_unit,
                                total_price=item_total
                            )
                        )
                contract.total_cost = calculated_total_cost

            # Обновление остальных полей шапки договора
            for key, value in update_data.items():
                setattr(contract, key, value)

            await uow.commit()
            
            contract = await uow.contract_repo.get_by_id_with_relations(item_id)
            return ContractResponse.model_validate(contract)

    # --- DELETE ---
    async def delete_contract(self, item_id: int) -> None:
        logger.info(f"Deleting contract ID: {item_id}")
        async with self.uow as uow:
            contract = await uow.contract_repo.get_by_id(item_id)
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
                
            await uow.contract_repo.delete(contract)
            await uow.commit()