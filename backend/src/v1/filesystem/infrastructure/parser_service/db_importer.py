# app/services/db_importer.py
import logging
from sqlalchemy import select

from backend.core.db.postgres.data_orms.contract_orm import Contract, ContractItem
from backend.core.db.postgres.data_orms.object_orm import Object
from backend.core.db.postgres.data_orms.work_orm import Work
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.data.domain.models import ContractStatus, ObjectStatus, WorkStatus



logger = logging.getLogger(__name__)


class DatabaseImporter:
    def __init__(self, uow: IUnitOfWork):
        self.uow = uow

    async def import_data(self, parsed_objects) -> None:
        """Импортирует дерево объектов в БД в рамках одной UOW-транзакции"""
        async with self.uow:
            for obj_dto in parsed_objects:
                # 1. Проверяем наличие Объекта в БД
                stmt_obj = select(Object).where(Object.title == obj_dto.title)
                res_obj = await self.uow.session.execute(stmt_obj)
                db_object = res_obj.scalar_one_or_none()

                if not db_object:
                    db_object = Object(
                        title=obj_dto.title,
                        address=obj_dto.address,
                        district=obj_dto.district,
                        status=ObjectStatus.PENDING
                    )
                    self.uow.session.add(db_object)
                    await self.uow.session.flush()

                # 2. Добавляем Работы
                for work_dto in obj_dto.works:
                    db_work = Work(
                        title=work_dto.title,
                        cost=work_dto.cost,
                        deadline=work_dto.deadline,
                        status=WorkStatus.PENDING,
                        object=db_object
                    )
                    self.uow.session.add(db_work)
                    await self.uow.session.flush()

                    # 3. Добавляем Контракты
                    for contract_dto in work_dto.contracts:
                        db_contract = Contract(
                            contract_id=contract_dto.contract_id,
                            date_signed=contract_dto.date_signed,
                            description=contract_dto.description,
                            status=ContractStatus.DRAFT,
                            cost=contract_dto.cost,
                            total_cost=contract_dto.total_cost,
                            planned_start=contract_dto.planned_start,
                            planned_end=contract_dto.planned_end,
                            object=db_object,
                            work=db_work
                        )
                        self.uow.session.add(db_contract)
                        await self.uow.session.flush()

                        # 4. Спецификация контракта
                        for item_dto in contract_dto.items:
                            db_item = ContractItem(
                                contract_id=db_contract.id,
                                title=item_dto.title,
                                quantity=item_dto.quantity,
                                unit=item_dto.unit,
                                price_per_unit=item_dto.price_per_unit,
                                total_price=item_dto.total_price
                            )
                            self.uow.session.add(db_item)
            
            # Фиксируем всю транзакцию разом!
            await self.uow.commit()