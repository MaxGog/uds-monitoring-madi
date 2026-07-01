from dataclasses import dataclass
import uuid

from fastapi import HTTPException, status

from backend.core.db.postgres.orm import Document, FileAccessType, RoleName
from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IUserRepo
from backend.src.v1.filesystem.domain.interfaces import IAwsService, IFileAuthUsecases, IFileRepo

@dataclass
class FileAuthUsecases(IFileAuthUsecases):
    uow: IUnitOfWork
    aws_service: IAwsService
    file_repo: IFileRepo
    user_repo: IUserRepo

    async def check_file_access(
            self,
            user_id: uuid.UUID,
            file_id: uuid.UUID,
            required_action: FileAccessType,
    ) -> bool:
        role = await self.user_repo.get_role(user_id)
        # Валидация для глобальных ролей, предполагается, что будут две глобальные роли - Admin, Viewer
        # Если будет что то другое - то будет отрабатывать сценарий пофайлового Access List
        if role == RoleName.ADMIN:
            return True
        if role == RoleName.VIEWER and required_action == FileAccessType.READ:
            return True
        
        file_exists = await self.file_repo.get_by_id(id = file_id)
        if not file_exists:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Файл не найден")
        
        # Если документ принадлежит пользователю, то у юзера есть право работы с файлом по дефолту
        if file_exists.owner_id == user_id:
            return True
        
        # Проверка индивидуальных прав в таблице file_permissions (ACL), но её ещё надо описать правильно в ORM
        # stmt = select(FilePermission).where(
        #     FilePermission.file_id == file_id,
        #     FilePermission.user_id == user_id,
        #     FilePermission.access_type == required_action
        # )
        # permission = await db.scalar(stmt)
        
        # if permission:
        #     return True

        # Если ни одно условие не выполнено — доступ запрещен
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Недостаточно прав для выполнения операции с этим файлом"
        )