from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index
from typing import Optional, List
from datetime import datetime
import uuid
from .base import BaseSQLModel, generate_uuid


class ConversationBase(SQLModel):
    title: Optional[str] = None


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    # Define indexes
    __table_args__ = (
        Index('idx_conversation_user_id', 'user_id'),
        Index('idx_conversation_created_at', 'created_at'),
    )

    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    user_id: uuid.UUID = Field(foreign_key="users.id")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to messages
    messages: List["Message"] = Relationship(back_populates="conversation")


class ConversationRead(ConversationBase):
    id: uuid.UUID
    user_id: uuid.UUID
    created_at: datetime
    updated_at: datetime


class ConversationCreate(ConversationBase):
    pass


class ConversationUpdate(SQLModel):
    title: Optional[str] = None