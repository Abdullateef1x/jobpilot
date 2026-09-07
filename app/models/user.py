import uuid
from datetime import datetime
from typing import TYPE_CHECKING

from pydantic import EmailStr
from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .application import Application

class UserBase(SQLModel):
    email: EmailStr = Field(unique=True, index=True)
    name: str
    is_active: bool  = Field(default=True) # Allows to ban or deactivate account


class UserCreate(UserBase):
        password: str # Plain text for signup form

class UserLogin(SQLModel):
      email: str
      password: str

class UserToken(SQLModel):
      access_token: str
      token_type: str

    
class User(UserBase, table= True):
    id: int| None = Field(default=None, primary_key= True)
    user_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)
    password_hash: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    current_resume_key: str | None = Field(default=None)
    applications: list["Application"] = Relationship(back_populates="user")      

class UserRead(UserBase):
        user_id: uuid.UUID
        created_at: datetime 

