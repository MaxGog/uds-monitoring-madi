import bcrypt

from backend.src.v1.auth.domain.interfaces import IPasswordHasher


class BCryptPasswordHash(IPasswordHasher):
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode('utf-8')
        password_hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
        return password_hash_bytes.decode('utf-8')
    
    def validate_password(self, password: str, hashed_password: str) -> bool:
        pwd_bytes: bytes = password.encode('utf-8')
        hashed_bytes = hashed_password.encode('utf-8')
        return bcrypt.checkpw(password=pwd_bytes, hashed_password=hashed_bytes)