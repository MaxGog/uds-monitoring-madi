import secrets

from pydantic_settings import BaseSettings


class CsrfSettings(BaseSettings):
    authjwt_secret_key: str = "fixed-super-secure-csrf-token-salt-2026"#secrets.token_hex(32) # не имеет отношения к JWT, но имеет отношение к authjwt модулю
    secret_key: str = "another-fixed-key-for-application"#secrets.token_hex(32)
    csrf_header_name: str = "X-CSRF-Token"
    csrf_cookie_name: str = "fastapi-csrf-token"
    csrf_cookie_is_secure: bool = False # True в прод, HTTPS 
    csrf_cookie_samesite: str = "lax"
    max_age: int = 7200
