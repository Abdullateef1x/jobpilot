import uuid
from datetime import datetime, timedelta, timezone
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from pwdlib import PasswordHash
from sqlmodel import Session

from app.config import setting
from app.core.database import get_session
from app.crud.user import get_user_by_uuid

ALGORITHM = "HS256"
ALGORITHMS = ["HS256"]

security = HTTPBearer()

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


def get_current_user(credentials: Annotated[HTTPAuthorizationCredentials, Depends(security)], db: Session = Depends(get_session)):
    token = credentials.credentials

    try:
        payload = jwt.decode(token, setting.SECRET_KEY, algorithms=ALGORITHMS)
        user_id = uuid.UUID(payload["sub"])
    except (JWTError, ValueError):
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    
    user = get_user_by_uuid(db, user_id)
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    
    if not user.is_active:
        raise HTTPException(status_code=401, detail="User has been deactivated")
    
    return user
 




