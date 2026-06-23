from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from enum import Enum

from fastapi import HTTPException, Request, Response


from backend.src.v1.auth.domain.interfaces import ITokenAuth, ITokenProvider, ITokenStorage
from backend.config.config import settings


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
            "jti": str(uuid6.uuid6())
            }
        jwt_payload.update(token_data)
        return self._encode_jwt(
            payload=jwt_payload,
            expire_minutes=expire_minutes,
            expire_timedelta=expire_timedelta,
            )         

    def extract_payload(self, token: str, verify_exp: bool = True) -> dict | None:
        """Публичный метод для безопасного извлечения данных из токена"""
        try:
            return self._decode_jwt(token, verify_exp=verify_exp)
        except jwt.PyJWTError as e:
            raise HTTPException(status_code=401, detail="Invalid Token")
        except jwt.InvalidTokenError:
            return HTTPException(status_code=401, detail="Invalid Token")

    def create_access_token(self, data: dict, jti: str) -> str:
        data["jti"] = jti
        return self._create_jwt(
            token_type=TokenType.ACCESS.value,
            token_data=data,
            expire_minutes=settings.auth_jwt.access_token_expire_minutes,
        )

    def create_refresh_token(self, data: dict, jti: str) -> str:
        data["jti"] = jti
        return self._create_jwt(
            token_type=TokenType.REFRESH.value,
            token_data=data,
            expire_timedelta=timedelta(days=settings.auth_jwt.refresh_token_expire_days),
        )
    
class TokenAuth(ITokenAuth):
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
    pass
