import logging

import bcrypt

from backend.src.v1.auth.domain.interfaces import IPasswordHasher

logger = logging.getLogger(__file__)


class BCryptPasswordHash(IPasswordHasher):
    
    def hash_password(self, password: str) -> str:
        try:
            salt = bcrypt.gensalt()
            pwd_bytes: bytes = password.encode('utf-8')
            password_hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
            return password_hash_bytes.decode('utf-8')
        except Exception as e:
            logger.error(e)

    def validate_password(self, password: str, hashed_password: str) -> bool:
        try:
            pwd_bytes: bytes = password.encode('utf-8')
            hashed_bytes = hashed_password.encode('utf-8')
            return bcrypt.checkpw(password=pwd_bytes, hashed_password=hashed_bytes)
        except Exception as e:
            logger.error(e)