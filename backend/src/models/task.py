from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, TYPE_CHECKING
from datetime import datetime
import uuid
from enum import Enum
from .base import BaseSQLModel, generate_uuid


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class TaskBase(SQLModel):
    title: str
    description: Optional[str] = None
    completed: bool = False
    due_date: Optional[datetime] = None
    # Make priority optional to handle existing records without this field
    priority: Optional[TaskPriority] = Field(default=TaskPriority.medium)
    # Make status optional to handle existing records without this field
    status: Optional[str] = Field(default="pending")


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    # Make priority column optional in the database
    priority: Optional[TaskPriority] = Field(default=TaskPriority.medium, nullable=True)
    # Make status column optional in the database
    status: Optional[str] = Field(default="pending", nullable=True)


class TaskRead(TaskBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime
    priority: TaskPriority = TaskPriority.medium


class TaskCreate(TaskBase):
    priority: Optional[TaskPriority] = TaskPriority.medium


class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    completed: Optional[bool] = None
    due_date: Optional[datetime] = None
    priority: Optional[TaskPriority] = None
    status: Optional[str] = None