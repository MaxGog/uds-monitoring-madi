from dataclasses import dataclass
import logging
from typing import List

from fastapi import HTTPException, status

from backend.core.db.postgres.data_orms.company_orm import Company
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.data.domain.interfaces import ICompanyRepo, ICompanyUsecases
from backend.src.v1.data.presentation.dtos.company_dto import CompanyCreateRequest, CompanyResponse, CompanyUpdateRequest

logger = logging.getLogger(__name__)

class CompanyUsecases(ICompanyUsecases):
    uow: IUnitOfWork
    company_repo: ICompanyRepo
    user_repo: IUserRepo

    # --- CREATE ---
    async def create_company(self, data: CompanyCreateRequest) -> CompanyResponse:
        logger.info(f"Registering new company: {data.name}")
        
        async with self.uow as uow:
            # Бизнес-валидация: Проверка уникальности ИНН (если он указан)
            if data.inn:
                existing = await uow.company_repo.get_by_inn(data.inn)
                if existing:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Company with INN {data.inn} already exists (ID: {existing.id})"
                    )

            new_company = Company(
                name=data.name,
                inn=data.inn,
                kpp=data.kpp,
                address=data.address,
                bank_account=data.bank_account,
                bank_name=data.bank_name,
                bic=data.bic
            )
            
            await uow.company_repo.add(new_company)
            await uow.commit()
            return CompanyResponse.model_validate(new_company)

    # --- READ (SINGLE) ---
    async def get_company_by_id(self, item_id: int) -> CompanyResponse:
        async with self.uow as uow:
            company = await uow.company_repo.get_by_id(item_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
            return CompanyResponse.model_validate(company)

    # --- READ (LIST) ---
    async def get_all_companies(self) -> List[CompanyResponse]:
        async with self.uow as uow:
            companies = await uow.company_repo.get_all()
            return [CompanyResponse.model_validate(c) for c in companies]

    # --- UPDATE (PATCH) ---
    async def update_company(self, item_id: int, data: CompanyUpdateRequest) -> CompanyResponse:
        logger.info(f"Updating item_id: {item_id}")
        
        async with self.uow as uow:
            company = await uow.company_repo.get_by_id(item_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")

            update_data = data.model_dump(exclude_unset=True)
            if not update_data:
                return CompanyResponse.model_validate(company)

            # Если меняется ИНН, проверяем его на дубликаты среди других компаний
            if "inn" in update_data and update_data["inn"] is not None:
                new_inn = update_data["inn"]
                if new_inn != company.inn:
                    existing = await uow.company_repo.get_by_inn(new_inn)
                    if existing:
                        raise HTTPException(
                            status_code=400,
                            detail=f"Company with INN {new_inn} already exists"
                        )

            # Применяем изменения
            for key, value in update_data.items():
                setattr(company, key, value)

            await uow.commit()
            
            # Обновляем объект перед маппингом
            company = await uow.company_repo.get_by_id(item_id)
            return CompanyResponse.model_validate(company)

    # --- DELETE ---
    async def delete_company(self, item_id: int) -> None:
        logger.info(f"Attempting to delete item_id: {item_id}")
        
        async with self.uow as uow:
            company = await uow.company_repo.get_by_id(item_id)
            if not company:
                raise HTTPException(status_code=404, detail="Company not found")
                
            # Защитный предохранитель: проверяем наличие привязанных пользователей
            # TODO: Но на уровне БД оставлен DELETE ALL CASCADE
            associated_users_count = await uow.users.count_by_company(item_id)
            if associated_users_count > 0:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=(
                        f"Cannot delete company. It has {associated_users_count} "
                        "active users. Reassign or delete them first."
                    )
                )

            await uow.company_repo.delete(company)
            await uow.commit()
            logger.info(f"Company {item_id} successfully deleted")