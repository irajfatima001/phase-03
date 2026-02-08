from sqlmodel import SQLModel, Field, Relationship
from sqlalchemy import Index
from typing import Optional
from datetime import datetime
import uuid
from enum import Enum
from .base import BaseSQLModel, generate_uuid


class MessageRole(str, Enum):
    user = "user"
    assistant = "assistant"


class MessageBase(SQLModel):
    conversation_id: uuid.UUID
    user_id: uuid.UUID
    role: MessageRole
    content: str


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    # Define indexes
    __table_args__ = (
        Index('idx_message_conversation_id', 'conversation_id'),
        Index('idx_message_user_id', 'user_id'),
        Index('idx_message_conversation_created_at', 'conversation_id', 'created_at'),
    )

    id: uuid.UUID = Field(default_factory=generate_uuid, primary_key=True)
    conversation_id: uuid.UUID = Field(foreign_key="conversations.id")
    user_id: uuid.UUID = Field(foreign_key="users.id")
    role: MessageRole = Field(sa_column_kwargs={"default": MessageRole.user})
    content: str = Field()
    created_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to conversation
    conversation: "Conversation" = Relationship(back_populates="messages")


class MessageRead(MessageBase):
    id: uuid.UUID
    created_at: datetime


class MessageCreate(MessageBase):
    pass