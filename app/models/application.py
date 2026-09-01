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
    job_description_url: str # Either make this an Enum of link or text for optimization reasons
    cover_letter: str | None = Field(default=None)


class ApplicationCreate(ApplicationBase):
    pass


class Application(ApplicationBase, table=True):
    id: int | None = Field(default=None, primary_key=True)
    application_id: uuid.UUID = Field(default_factory=uuid.uuid4, unique=True, index=True)  
    user_id: int = Field(foreign_key="user.id")
    job_description: str | None = None
    user: Optional["User"]= Relationship(back_populates="applications")



class ApplicationRead(ApplicationBase):
    application_id: uuid.UUID
    match_score: float
    match_explanation: str
    created_at: datetime 


