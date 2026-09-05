from datetime import datetime, timedelta, timezone

from jose import jwt
from pwdlib import PasswordHash

from app.config import setting

ALGORITHM = "HS256"


password_hash = PasswordHash.recommended()

def hash_password(password: str) -> str:
    return password_hash.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return password_hash.verify(plain_password, hashed_password) 

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()

    if "sub" in to_encode:
        to_encode["sub"] = str(to_encode["sub"])

    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    to_encode.update({"exp": expire })
    encoded_jwt = jwt.encode(to_encode, setting.SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt



 




