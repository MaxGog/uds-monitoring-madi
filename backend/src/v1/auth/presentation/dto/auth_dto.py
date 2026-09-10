from dataclasses import dataclass

from backend.src.v1.auth.domain.models import UserModel


@dataclass
class RefreshSessionDTO:
    access_token: str
    refresh_token: str

@dataclass
class LoginResultDTO:
    access_token: str
    refresh_token: str
    user: UserModel