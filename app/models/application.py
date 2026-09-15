import uuid
from datetime import datetime
from enum import Enum
from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from .user import User


class ApplicationStatus(str, Enum):
    Applied = "applied"
    Interviewed = "interviewed"
    Rejected = "rejected"
    Offered = "offered"


class ApplicationBase(SQLModel):
    role_title: str
    company_name: str
    status: ApplicationStatus # applied, interviewed, rejected, offered
    job_description_url: str | None = None 
    job_description: str 
    cover_letter: str | None = Field(default=None)


class ApplicationCreate(ApplicationBase):
    job_description: str


class Application(ApplicationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    application_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)  
    user_id: int = Field(foreign_key="user.id")
    user: Optional["User"]= Relationship(back_populates="applications")
    job_description: str 
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    match_score: float | None = None 
    match_explanation: str | None = None


class ApplicationRead(ApplicationBase):
    application_id: uuid.UUID
    match_score: float | None = None
    match_explanation: str | None = None
    created_at: datetime
    updated_at: datetime 


class ApplicationStatusUpdate(SQLModel):
    status: ApplicationStatus