from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum
import uuid6
import logging
from fastapi import HTTPException, Request, Response
import jwt

from backend.src.v1.auth.domain.interfaces import ITokenAuth, ITokenProvider, ITokenStorage
from backend.config.config import settings

logger = logging.getLogger("jwt_service")

TOKEN_TYPE_FIELD = "type"

class TokenType(str, Enum):
    ACCESS = "access"
    REFRESH = "refresh"

@dataclass
class TokenData():
    access_token: str
    refresh_token: str | None = None
    token_type: str = "Bearer"


class TokenProvider(ITokenProvider):
    '''
    Данный класс служит только для создания, чтения и встроенной валидации JWT токенов.
    '''
    def _encode_jwt(
            self,
            payload: dict,
            private_key: str = settings.auth_jwt.private_key_path.read_text(),
            algorithm: str = settings.auth_jwt.algorithm,
            expire_minutes: int = 5,
            expire_timedelta: timedelta | None = None,
        ) -> str:
        to_encode: dict = payload.copy()

        now = datetime.now(timezone.utc)
        if expire_timedelta:
            expire = now + expire_timedelta
        else:
            expire = now + timedelta(minutes = expire_minutes)

        to_encode.update(
            exp=expire,
            iat=now,
        )

        encoded = jwt.encode(
            to_encode,
            private_key,
            algorithm=algorithm,
        )
        return encoded

    def _decode_jwt(
            self,
            token: str | bytes,
            public_key: str = settings.auth_jwt.public_key_path.read_text(),
            algorithm: str = settings.auth_jwt.algorithm,
            verify_exp: bool = True
    ) -> dict:
        decoded = jwt.decode(
            token,
            public_key,
            algorithms=algorithm,
            options={"verify_exp": verify_exp}
        )
        return decoded

    def _create_jwt(
            self,
            token_type: str,
            token_data: dict,
            expire_minutes: int = settings.auth_jwt.access_token_expire_minutes,
            expire_timedelta: timedelta | None = None,
            ) -> str:
        jwt_payload = {
            TOKEN_TYPE_FIELD: token_type,
            "jti": str(uuid6.uuid6()),
            "aud": "frontend",      # кто получает токен - в нашем случае это фронтенд клиент, но можно и мобильный
            "iss": "auth.app.local" # если архитектура микросервисная, то здесь будет доменное имя микросервиса
            }
        jwt_payload.update(token_data)
        return self._encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
            )         

    def extract_payload(self, token: str, verify_exp: bool = True) -> dict | None:
        """
        Публичный метод для безопасного извлечения данных из токена
        verify_exp: нужен для механизма ротации токенов, т.к. для этого передаются оба токена,
        один из которых не пройдёт проверку на валидность, а другой пройдёт (access и refresh токен соответственно).
        """
        try:
            return self._decode_jwt(token, verify_exp=verify_exp)
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid Token")
        except jwt.InvalidTokenError:
            return HTTPException(status_code=401, detail="Invalid Token")

    def create_access_token(self, data: dict) -> str:
        return self._create_jwt(
            token_type=TokenType.ACCESS.value,
            token_data=data,
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    def create_refresh_token(self, data: dict) -> str:
        return self._create_jwt(
            token_type=TokenType.REFRESH.value,
            token_data=data,
            expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
        )
    
class TokenAuth(ITokenAuth):
    '''
    Данный класс оркестрирует генерацию, валидацию, хранение токенов.
    '''
    def __init__(
            self,
            token_provider: ITokenProvider,
            token_storage: ITokenStorage,
            request: Request | None = None,
            response: Response | None = None,
            ):
        self.token_provider = token_provider
        self.token_storage = token_storage
        self.request = request
        self.response = response

    async def set_tokens(self, user_id: int | None = None) -> TokenData:
        '''
        
        '''       
        data = {
            "sub": str(user_id),
        }

        access_token = self.token_provider.create_access_token(data)
        refresh_token = self.token_provider.create_refresh_token(data)

        payload = self.token_provider.extract_payload(refresh_token)
        expire_seconds = int(payload["exp"] - payload["iat"])

        await self.token_storage.add_session(
            user_id=user_id,
            access_jti=access_jti,
            refresh_jti=refresh_jti,
            expire_seconds=expire_seconds
            )

        result = TokenData(
            access_token=access_token,
            refresh_token=refresh_token,
            )  
        return result

    async def set_token(self, token: str, token_type: TokenType):
        pass
    
    async def rotate_tokens(self, user_id: int, old_access_token: str, old_refresh_token: str) -> TokenData:
        old_access_payload = self.token_provider.extract_payload(old_access_token, verify_exp = False)
        old_refresh_payload = self.token_provider.extract_payload(old_refresh_token)

        if not old_access_payload or not old_refresh_payload:
            raise HTTPException(status_code=401, detail="Invalid token")

        old_storage_value = f"{old_access_payload['jti']}:{old_refresh_payload['jti']}"
        new_access_jti = str(uuid6.uuid6())
        new_refresh_jti = str(uuid6.uuid6())

        new_access_token = self.token_provider.create_access_token(data={"sub": str(user_id) }, jti = new_access_jti)
        new_refresh_token = self.token_provider.create_refresh_token(data={"sub": str(user_id) }, jti = new_refresh_jti)

        new_storage_value = f"{new_access_jti}:{new_refresh_jti}"

        expire_seconds = self.get_expire_seconds(token=new_refresh_token, verify_exp=False)

        await self.token_storage.rotate_session(user_id, old_storage_value, new_storage_value, expire_seconds)

        return TokenData(
            access_token=new_access_token,
            refresh_token=new_refresh_token
        )

    #TODO Переделать код, т.к. не должна быть лютая логика в хранилище токенов, а должна быть в сервисе аутентификации, а хранилище должно просто хранить токены и проверять их наличие
    async def revoke_specific_session(self, access_token: str, refresh_token: str):
        access_payload = self.token_provider.extract_payload(access_token, verify_exp = False)
        refresh_payload = self.token_provider.extract_payload(refresh_token)
        a_jti = access_payload["jti"]
        r_jti = refresh_payload["jti"]
        if a_jti and r_jti:
            user_id = int(refresh_payload["sub"])
            await self.token_storage.remove_session(
                user_id=user_id, 
                a_jti=a_jti, 
                r_jti=r_jti
            )

    async def revoke_all_sessions(self, user_id: int) -> None:
        await self.token_storage.remove_all_sessions(user_id)

    async def is_token_valid(self, access_token: str) -> bool:
        payload = self.token_provider.extract_payload(access_token)

        user_id = int(payload.get("sub"))
        a_jti = payload.get("jti")
        is_valid = await self.token_storage.is_token_valid(user_id, a_jti)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Session revoked or expired")
        return True

    async def is_session_valid(self, access_token: str, refresh_token: str) -> bool:
        payload = self.token_provider.extract_payload(access_token, verify_exp = False)

        user_id = int(payload.get("sub"))
        a_jti = payload.get("jti")
        r_jti = self.token_provider.extract_payload(refresh_token).get("jti")
        # Проверка Stateful (есть ли токен в белом списке Redis)
        is_valid = await self.token_storage.is_session_valid(user_id, a_jti, r_jti)
        if not is_valid:
            raise HTTPException(status_code=401, detail="Session revoked or expired")
            
        return True

    async def revoke_specific_token_by_user_id(self, user_id: int, token: TokenData) -> None:
        await self.token_storage.revoke_specific_token_by_user_id(user_id, token)

    def get_expire_seconds(self, token: str, verify_exp: bool = True) -> int | None:
        payload = self.token_provider.extract_payload(token, verify_exp = verify_exp)
        if payload:
            exp = payload.get("exp")
            iat = payload.get("iat")
            if exp and iat:
                return int(exp - iat)
        return None
    
    def _get_access_token(self) -> str | None:
        if hasattr(self.request.state, "access_token"):
            return self.request.state.access_token

    def _get_refresh_token(self) -> str | None:
        if hasattr(self.request.state, "refresh_token"):
            return self.request.state.refresh_token  

    def _validate_token(self, token: str) -> dict | None:
        try:
            if self.token_storage:
                payload = self.token_provider._decode_jwt(token)
            jti = payload.get("jti")

            if token.token_storage:
                client = self.token_storage.client()
            if client.exists(f"allowlist:{jti}"):
                raise HTTPException(status_code=401, detail="Token has been revoked")
                
            return payload
        except Exception:
            raise HTTPException(status_code=401, detail="Invalid token")
