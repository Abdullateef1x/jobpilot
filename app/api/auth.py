from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.config import ACCESS_TOKEN_EXPIRES_MINUTES
from app.core.database import get_session
from app.core.security import create_access_token, verify_password
from app.crud.user import create_user, get_user_by_email
from app.models.user import UserCreate, UserLogin, UserRead, UserToken

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/register", response_model=UserRead)
async def register(payload: UserCreate, db: Session = Depends(get_session)):

    existing_user = get_user_by_email(db, payload.email)

    if existing_user:
        raise HTTPException(status_code=401, detail="Email alraedy registered")

            
    user = create_user(db, payload)
    return user




@router.post("/login", response_model=UserToken)
async def login(payload: UserLogin, db: Session = Depends(get_session)):
    existing_user = get_user_by_email(db, payload.email)

    if existing_user is None:
        raise HTTPException(status_code=401, detail="User not found")
    
    hashed_password = existing_user.password_hash 

    verified = verify_password(payload.password, hashed_password)

    if verified == False:
        raise HTTPException(status_code=401, detail="User not found")
    
    access_token_expires = timedelta(minutes=ACCESS_TOKEN_EXPIRES_MINUTES)
    access_token = create_access_token(
        data={"sub": existing_user.user_id}, expires_delta=access_token_expires
    )
    
    return UserToken(access_token=access_token, token_type="Bearer")