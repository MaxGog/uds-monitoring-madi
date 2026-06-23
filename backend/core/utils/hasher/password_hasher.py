import bcrypt


class BCryptPasswordHash(IPasswordHasher):
    
    def hash_password(self, password: str) -> str:
        salt = bcrypt.gensalt()
        pwd_bytes: bytes = password.encode('utf-8')
        password_hash_bytes = bcrypt.hashpw(pwd_bytes, salt)
        return password_hash_bytes.decode('utf-8')
    
    def validate_password(self, password: str, hashed_password: str) -> bool:
        return bcrypt.checkpw(password=password.encode(), hashed_password=hashed_password.encode())