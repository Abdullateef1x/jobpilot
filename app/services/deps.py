import uuid
from typing import Annotated

from fastapi import Depends, HTTPException
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jose import JWTError, jwt
from sqlmodel import Session

from app.config import setting
from app.core.database import get_session
from app.crud.user import get_user_by_uuid

ALGORITHMS = ["HS256"]

security = HTTPBearer()


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