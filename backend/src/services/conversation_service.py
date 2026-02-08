from sqlmodel import Session, select
from typing import List, Optional
from datetime import datetime
import uuid
from src.models.conversation import Conversation, ConversationCreate
from src.models.message import Message, MessageCreate, MessageRole
from src.core.logging_config import get_logger


logger = get_logger(__name__)


class ConversationService:
    def __init__(self):
        pass

    async def create_conversation(self, db_session: Session, user_id: uuid.UUID, conversation_data: ConversationCreate) -> Conversation:
        """
        Create a new conversation
        """
        try:
            conversation = Conversation(
                user_id=user_id,
                title=conversation_data.title,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            db_session.add(conversation)
            db_session.commit()
            db_session.refresh(conversation)
            logger.info(f"Created conversation {conversation.id} for user {user_id}")
            return conversation
        except Exception as e:
            logger.error(f"Error creating conversation for user {user_id}: {str(e)}")
            raise e

    async def get_conversation_by_id(self, db_session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> Optional[Conversation]:
        """
        Get a conversation by ID for a specific user
        """
        try:
            statement = select(Conversation).where(
                Conversation.id == conversation_id,
                Conversation.user_id == user_id
            )
            conversation = db_session.exec(statement).first()
            if conversation:
                logger.info(f"Fetched conversation {conversation_id} for user {user_id}")
            else:
                logger.warning(f"Conversation {conversation_id} not found for user {user_id}")
            return conversation
        except Exception as e:
            logger.error(f"Error fetching conversation {conversation_id} for user {user_id}: {str(e)}")
            raise e

    async def verify_user_owns_conversation(self, db_session: Session, conversation_id: uuid.UUID, user_id: uuid.UUID) -> bool:
        """
        Verify that the user owns the specified conversation
        """
        try:
            conversation = await self.get_conversation_by_id(db_session, conversation_id, user_id)
            owns_conversation = conversation is not None
            if not owns_conversation:
                logger.warning(f"User {user_id} attempted to access conversation {conversation_id} which does not belong to them")
            return owns_conversation
        except Exception as e:
            logger.error(f"Error verifying ownership of conversation {conversation_id} for user {user_id}: {str(e)}")
            return False

    async def log_access_attempt(self, user_id: uuid.UUID, resource_type: str, resource_id: str, action: str, success: bool):
        """
        Log access attempts for audit purposes
        """
        status = "SUCCESS" if success else "FAILED"
        logger.info(f"AUDIT: User {user_id} {action} {status} on {resource_type} {resource_id}")

    async def get_user_conversations(self, db_session: Session, user_id: uuid.UUID) -> List[Conversation]:
        """
        Get all conversations for a user
        """
        try:
            statement = select(Conversation).where(Conversation.user_id == user_id)
            conversations = db_session.exec(statement).all()
            logger.info(f"Fetched {len(conversations)} conversations for user {user_id}")
            return conversations
        except Exception as e:
            logger.error(f"Error fetching conversations for user {user_id}: {str(e)}")
            raise e

    async def add_message_to_conversation(
        self, 
        db_session: Session, 
        conversation_id: uuid.UUID, 
        user_id: uuid.UUID, 
        content: str, 
        role: MessageRole
    ) -> Message:
        """
        Add a message to a conversation
        """
        try:
            message = Message(
                conversation_id=conversation_id,
                user_id=user_id,
                role=role,
                content=content,
                created_at=datetime.utcnow()
            )
            db_session.add(message)
            # Update conversation's updated_at timestamp
            try:
                conversation = await self.get_conversation_by_id(db_session, conversation_id, user_id)
                if conversation:
                    conversation.updated_at = datetime.utcnow()
                    db_session.add(conversation)
            except Exception as e:
                logger.warning(f"Could not update conversation timestamp: {str(e)}")
                # Continue anyway, this is not critical

            db_session.commit()
            db_session.refresh(message)
            logger.info(f"Added message to conversation {conversation_id} for user {user_id}")
            return message
        except Exception as e:
            logger.error(f"Error adding message to conversation {conversation_id}: {str(e)}")
            raise e

    async def get_messages_for_conversation(
        self,
        db_session: Session,
        conversation_id: uuid.UUID,
        user_id: uuid.UUID
    ) -> List[Message]:
        """
        Get all messages for a specific conversation
        """
        try:
            statement = select(Message).where(
                Message.conversation_id == conversation_id,
                Message.user_id == user_id
            ).order_by(Message.created_at.asc())
            messages = db_session.exec(statement).all()
            logger.info(f"Fetched {len(messages)} messages for conversation {conversation_id}")
            return messages
        except Exception as e:
            logger.error(f"Error fetching messages for conversation {conversation_id}: {str(e)}")
            raise e

    async def get_conversation_history(
        self,
        db_session: Session,
        user_id: uuid.UUID,
        limit: int = 10
    ) -> List[Conversation]:
        """
        Get recent conversation history for a user
        """
        try:
            statement = select(Conversation).where(
                Conversation.user_id == user_id
            ).order_by(Conversation.updated_at.desc()).limit(limit)
            conversations = db_session.exec(statement).all()
            logger.info(f"Fetched {len(conversations)} recent conversations for user {user_id}")
            return conversations
        except Exception as e:
            logger.error(f"Error fetching conversation history for user {user_id}: {str(e)}")
            raise e