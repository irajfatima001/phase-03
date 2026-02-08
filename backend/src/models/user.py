from sqlmodel import SQLModel, Field
from datetime import datetime
import uuid
from .base import BaseSQLModel, generate_uuid


class UserBase(SQLModel):
    email: str
    name: str


class User(UserBase, table=True):
    __tablename__ = "users"

    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    email: str = Field(unique=True, nullable=False)
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)


class UserRead(UserBase):
    id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class UserCreate(UserBase):
    password: str  # In a real app, this would be hashed