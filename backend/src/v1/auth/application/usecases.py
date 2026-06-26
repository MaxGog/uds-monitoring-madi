import base64
from dataclasses import dataclass
import hashlib
from typing import Optional

from fastapi import HTTPException

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, ITokenAuth, ITokenStorage, IUserRepository
from backend.src.v1.auth.domain.models import LoginResultDTO
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateDTO, UserResponseDTO


@dataclass
class AuthUsecases:
    """
    Единая точка входа для всех бизнес-сценариев (Use Cases) модуля Auth.
    Сюда через DI (или конструктор) прилетают нужные инфраструктурные репозитории и сервисы.
    """
    uow: IUnitOfWork
    token_repo: ITokenStorage
    token_service: ITokenAuth
    hasher: IPasswordHasher

    async def register_new_user(self, dto: UserCreateDTO) -> UserResponseDTO:
        """Юзкейс 1: Регистрация"""
        async with self.uow:
            existing_user = await self.uow.users.get_by_email(dto.email)
            if existing_user:
                raise HTTPException(status_code=409, detail='username or email already exists')
            password_hash_str = self.hasher.hash_password(dto.password)
            dto.password = password_hash_str
            user = await self.uow.users.create_user(dto)
        return user

    async def validate_user_credentials(self, email: str, password: str) -> Optional[UserResponseDTO]:
        """Юзкейс 2: Проверка логина/пароля перед выдачей OAuth2 Code"""
        user = await self.user_repo.get_by_email(email)
        # if not user or not user.check_password(password):
        #     return None
        return UserResponseDTO.from_attributes(user)

    async def exchange_code_for_tokens(self, code: str, code_verifier: str) -> LoginResultDTO:
        """Юзкейс 3: Обмен OAuth2 Authorization Code на JWT (Access/Refresh)"""
        code_data = await self.token_repo.get_and_delete_code(code)
        if not code_data:
            raise ValueError("Invalid or expired code")
        
        if not self._verify_pkce(code_verifier, code_data.challenge):
            raise ValueError("PKCE validation failed")

        return await self.token_service.set_tokens(code_data.user_id)
    
    def _verify_pkce(self, verifier: str, challenge: str) -> bool:
        digest = hashlib.sha256(verifier.encode('utf-8')).digest()
        expected = base64.urlsafe_b64encode(digest).decode('utf-8').rstrip('=')
        return challenge == expected
        
    async def refresh_session(self, refresh_token: str) -> LoginResultDTO:
        """Юзкейс 4: Обновление протухшего Access-токена"""
        pass