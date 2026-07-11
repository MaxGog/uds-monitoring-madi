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
    def __init__(self, uow: IUnitOfWork, contract_repo: IContractRepo, user_repo: IUserRepo) -> None:
        self.uow = uow
        self.contract_repo = contract_repo
        self.user_repo = user_repo

    # --- READ (SINGLE) ---
    async def get_contract_by_id(self, item_id: int) -> ContractResponse:
        try:
            contract = await self.contract_repo.get_by_id_with_relations(item_id)
            if not contract:
                raise HTTPException(status_code=404, detail="Contract not found")
            return ContractResponse.model_validate(contract)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- READ (LIST) ---
    async def get_all_contracts(self) -> List[ContractResponse]:
        try:
            contracts = await self.contract_repo.get_all()
            return [ContractResponse.model_validate(c) for c in contracts]
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- CREATE ---
    async def create_contract(self, data: ContractCreateRequest) -> ContractResponse:
        logger.info(f"Creating contract: {data.contract_id}")
        create_data = data.model_dump(exclude_none=True, exclude_unset=True)
        try:
            async with self.uow as uow:
                # Проверка внешних ключей
                object_id = create_data.get('object_id')
                if object_id and not await uow.object_repo.get_by_id(object_id):
                    raise HTTPException(status_code=400, detail=f"Object {object_id} not found")
                
                work_id = create_data.get('work_id')
                if work_id and not await uow.work_repo.get_by_id(work_id):
                    raise HTTPException(status_code=400, detail=f"Work {work_id} not found")

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
                    **create_data
                )

                await uow.contract_repo.add(new_contract)
                await uow.commit()
                
                contract = await uow.contract_repo.get_by_id_with_relations(new_contract.id)
                return ContractResponse.model_validate(contract)
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)


    # --- UPDATE (PATCH) ---
    async def update_contract(self, item_id: int, data: ContractUpdateRequest) -> ContractResponse:
        logger.info(f"Patching contract ID: {item_id}")
        try:
            async with self.uow as uow:
                contract = await uow.contract_repo.get_by_id_with_relations(item_id)
                if not contract:
                    raise HTTPException(status_code=404, detail="Contract not found")

                update_data = data.model_dump(exclude_unset=True, exclude_none=True)
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
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
    # --- DELETE ---
    async def delete_contract(self, item_id: int) -> None:
        logger.info(f"Deleting contract ID: {item_id}")
        try:
            async with self.uow as uow:
                contract = await uow.contract_repo.get_by_id(item_id)
                if not contract:
                    raise HTTPException(status_code=404, detail="Contract not found")
                    
                await uow.contract_repo.delete(contract)
                await uow.commit()
        except HTTPException as e:
            logger.error(e)
            raise e
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)