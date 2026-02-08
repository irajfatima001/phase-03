from sqlmodel import Session, create_engine, select
from fastapi import Depends, HTTPException, status
from src.core.config import settings
from src.core.security import get_current_user
import uuid
from src.models.task import Task
from src.models.conversation import Conversation
from src.models.message import Message


# Create the database engine
engine = create_engine(settings.DATABASE_URL)


from fastapi import Depends
from typing import Generator
from sqlmodel import Session


def get_db_session() -> Generator[Session, None, None]:
    """
    Dependency function for FastAPI to get a database session
    """
    with Session(engine) as session:
        yield session


def verify_user_owns_task(db_session: Session, task_id: str, user_id: uuid.UUID) -> bool:
    """
    Verify that the user owns the specified task
    """
    task = db_session.get(Task, uuid.UUID(task_id))
    if not task or task.user_id != user_id:
        return False
    return True


def verify_user_owns_conversation(db_session: Session, conversation_id: str, user_id: uuid.UUID) -> bool:
    """
    Verify that the user owns the specified conversation
    """
    conversation = db_session.get(Conversation, uuid.UUID(conversation_id))
    if not conversation or conversation.user_id != user_id:
        return False
    return True


def verify_user_owns_message(db_session: Session, message_id: str, user_id: uuid.UUID) -> bool:
    """
    Verify that the user owns the specified message
    """
    message = db_session.get(Message, uuid.UUID(message_id))
    if not message or message.user_id != user_id:
        return False
    return True


def require_user_ownership_of_task(task_id: str, current_user_id: uuid.UUID = Depends(get_current_user), db_session: Session = Depends(get_db_session)):
    """
    Dependency to verify that the current user owns the specified task
    """
    if not verify_user_owns_task(db_session, task_id, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this task"
        )
    return current_user_id


def require_user_ownership_of_conversation(conversation_id: str, current_user_id: uuid.UUID = Depends(get_current_user), db_session: Session = Depends(get_db_session)):
    """
    Dependency to verify that the current user owns the specified conversation
    """
    if not verify_user_owns_conversation(db_session, conversation_id, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this conversation"
        )
    return current_user_id


def require_user_ownership_of_message(message_id: str, current_user_id: uuid.UUID = Depends(get_current_user), db_session: Session = Depends(get_db_session)):
    """
    Dependency to verify that the current user owns the specified message
    """
    if not verify_user_owns_message(db_session, message_id, current_user_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access denied: You don't have permission to access this message"
        )
    return current_user_id


# Dependency for getting the current user
CurrentUser = Depends(get_current_user)

# Dependency for getting the database session
# Note: Use get_db_session directly with Depends() to avoid double wrapping