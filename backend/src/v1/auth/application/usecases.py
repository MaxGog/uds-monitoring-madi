import base64
from dataclasses import dataclass
import hashlib
import logging
import secrets
from typing import Optional

from fastapi import HTTPException, status

from backend.core.db.postgres.unit_of_work import IUnitOfWork
from backend.src.v1.auth.domain.interfaces import IPasswordHasher, ITokenAuth, ITokenProvider, ITokenStorage
from backend.src.v1.auth.presentation.dto.auth_dto import LoginResultDTO, RefreshSessionDTO
from backend.src.v1.auth.presentation.dto.user_dto import UserCreateDTO, UserResponseDTO

logger = logging.getLogger(__file__)

@dataclass
class AuthUsecases:
    """
    Единая точка входа для всех бизнес-сценариев (Use Cases) модуля Auth.
    Сюда через DI (или конструктор) прилетают нужные инфраструктурные репозитории и сервисы.
    """
    uow: IUnitOfWork
    token_repo: ITokenStorage
    token_service: ITokenAuth
    token_provider: ITokenProvider
    hasher: IPasswordHasher

    async def register_new_user(self, dto: UserCreateDTO) -> UserResponseDTO:
        """Юзкейс 1: Регистрация"""
        async with self.uow as uow:
            existing_user = await uow.users.get_by_email(dto.email)
            if existing_user:
                raise HTTPException(status_code=409, detail='username or email already exists')
            password_hash_str = self.hasher.hash_password(dto.password)
            dto.password = password_hash_str
            user = await uow.users.create_user(dto)
        return user

    async def login(self, email: str, password: str, code_challenge: str) -> str:
        """Юзкейс 2: Проверка логина/пароля перед выдачей OAuth2 Code"""
        user = await self._validate_user_credentials(email=email, password=password)
        auth_code = secrets.token_urlsafe(32)
        result = await self.token_repo.save_code(
            code=auth_code,
            user_id=str(user.id),
            challenge=code_challenge
        )
        if not result:
            raise HTTPException(status_code=403, detail='Invalid data')
        return auth_code

    async def _validate_user_credentials(self, email: str, password: str) -> Optional[UserResponseDTO]:
        async with self.uow:
            user = await self.uow.users.get_by_email(email)
        if not user:
            raise HTTPException(status_code=409, detail='Incorrect email or password')
        is_password_valid = await self._check_password(pwd_hash=user.pwdhash, password=password)
        if not is_password_valid:
            raise HTTPException(status_code=409, detail='Incorrect email or password')
        return user
    
    async def _check_password(self, pwd_hash, password):
        return self.hasher.validate_password(password=password, hashed_password=pwd_hash)

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
        
    async def rotate_tokens(self, refresh_token: str, access_token: str | None = None) -> RefreshSessionDTO:
        """Юзкейс 4: Обновление протухшего Access-токена"""
        try:
            await self.token_service.is_session_valid(access_token = access_token, refresh_token = refresh_token)

            old_payload = self.token_provider.extract_payload(refresh_token)
            user_id = str(old_payload.get("sub"))

            new_tokens = await self.token_service.rotate_tokens(
                user_id,
                old_access_token=access_token,
                old_refresh_token=refresh_token
            )
            return new_tokens
        except HTTPException as e:
            logger.error(e)
            raise HTTPException(status_code=401, detail="Invalid token")
        except Exception as e:
            logger.error(e)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)