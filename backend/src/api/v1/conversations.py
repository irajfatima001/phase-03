from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session
from src.models.conversation import Conversation, ConversationCreate, ConversationRead
from src.models.message import Message, MessageCreate, MessageRead, MessageRole
from src.models.message import Message as MessageModel  # Renaming to avoid conflict
from pydantic import BaseModel
from pydantic import Field
from src.services.conversation_service import ConversationService
from src.api.deps import CurrentUser, get_db_session
from fastapi import Depends
from src.core.logging_config import get_logger
from src.core.config import settings
import uuid
import cohere
from datetime import datetime


# Define a model for the initiate request that only requires content
class InitiateConversationRequest(BaseModel):
    content: str


# Define a model for adding messages that only requires content
class AddMessageRequest(BaseModel):
    content: str


router = APIRouter()
logger = get_logger(__name__)
conversation_service = ConversationService()


@router.get("/conversations", response_model=List[ConversationRead])
async def get_conversations(
    current_user_id: uuid.UUID = CurrentUser,
    db_session: Session = Depends(get_db_session)
):
    """
    Retrieve all conversations for the current user
    """
    try:
        conversations = await conversation_service.get_user_conversations(
            db_session, current_user_id
        )
        logger.info(f"User {current_user_id} retrieved {len(conversations)} conversations")
        return conversations
    except Exception as e:
        logger.error(f"Error retrieving conversations for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversations: {str(e)}"
        )


@router.get("/conversations/{conversation_id}", response_model=dict)  # Using dict to return conversation with messages
async def get_conversation(
    conversation_id: str,
    current_user_id: uuid.UUID = CurrentUser,
    db_session: Session = Depends(get_db_session)
):
    """
    Retrieve a specific conversation and its messages
    """
    try:
        conv_id = uuid.UUID(conversation_id)

        # Verify user owns the conversation
        from src.api.deps import verify_user_owns_conversation
        if not verify_user_owns_conversation(db_session, conversation_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to access this conversation"
            )

        conversation = await conversation_service.get_conversation_by_id(
            db_session, conv_id, current_user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Get messages for this conversation
        messages = await conversation_service.get_messages_for_conversation(
            db_session, conv_id, current_user_id
        )

        logger.info(f"User {current_user_id} retrieved conversation {conversation_id}")

        # Return conversation with its messages
        return {
            "id": str(conversation.id),
            "title": conversation.title,
            "created_at": conversation.created_at,
            "updated_at": conversation.updated_at,
            "messages": [
                {
                    "id": str(m.id),
                    "role": m.role,
                    "content": m.content,
                    "created_at": m.created_at
                }
                for m in messages
            ]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving conversation {conversation_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving conversation: {str(e)}"
        )


@router.post("/conversations", response_model=ConversationRead)
async def create_conversation(
    conversation_data: ConversationCreate,
    current_user_id: uuid.UUID = CurrentUser,
    db_session: Session = Depends(get_db_session)
):
    """
    Create a new conversation
    """
    try:
        conversation = await conversation_service.create_conversation(
            db_session, current_user_id, conversation_data
        )
        logger.info(f"User {current_user_id} created conversation {conversation.id}")
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating conversation: {str(e)}"
        )


@router.post("/conversations/initiate", response_model=dict)
async def initiate_conversation(
    request_data: InitiateConversationRequest,
    current_user_id: uuid.UUID = CurrentUser,
    db_session: Session = Depends(get_db_session)
):
    """
    Initiate a new conversation with a message
    """
    try:
        # Check if the user wants to perform a task operation
        content_lower = request_data.content.lower()

        # Check for task operations
        import re

        # Check for task creation
        if any(keyword in content_lower for keyword in ['add task', 'create task', 'new task']):
            # Extract task information from the request
            task_match = re.search(r'(?:add task|create task|new task)[:\-]?\s*(.+?)(?:\s+with\s+description\s+(.+?))?(?=\s+[.!?]|$)', request_data.content, re.IGNORECASE)

            if task_match:
                title = task_match.group(1).strip()
                description = task_match.group(2).strip() if task_match.group(2) else None

                # Create the task
                task_data = TaskCreate(
                    title=title,
                    description=description,
                    completed=False
                )

                # Import here to avoid circular imports
                from src.api.v1.tasks import create_task
                created_task = await create_task(task_data, db_session, current_user_id)

                # Create a new conversation
                title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                conversation_data = ConversationCreate(title=title_conv)
                conversation = await conversation_service.create_conversation(
                    db_session, current_user_id, conversation_data
                )

                # Add the initial message to the conversation
                user_message = await conversation_service.add_message_to_conversation(
                    db_session,
                    conversation.id,
                    current_user_id,
                    request_data.content,
                    "user"
                )

                # Get updated task list
                from src.api.v1.tasks import get_tasks
                updated_tasks = await get_tasks(db_session, current_user_id)

                # Create AI response message
                ai_message = Message(
                    conversation_id=conversation.id,
                    user_id=current_user_id,
                    role=MessageRole.assistant,
                    content=f"I've created the task '{created_task.title}' for you successfully!",
                    created_at=datetime.utcnow()
                )
                db_session.add(ai_message)
                db_session.commit()
                db_session.refresh(ai_message)

                logger.info(f"User {current_user_id} initiated conversation {conversation.id} and created task {created_task.id}")

                return {
                    "conversation_id": str(conversation.id),
                    "user_message": MessageRead(
                        conversation_id=user_message.conversation_id,
                        user_id=user_message.user_id,
                        role=user_message.role,
                        content=user_message.content,
                        id=user_message.id,
                        created_at=user_message.created_at
                    ),
                    "ai_response": {
                        "id": str(ai_message.id),
                        "role": ai_message.role,
                        "content": ai_message.content,
                        "created_at": ai_message.created_at
                    },
                    "updated_tasks": updated_tasks  # Include updated task list
                }

        # Check for listing tasks
        elif any(keyword in content_lower for keyword in ['show my tasks', 'list tasks', 'view tasks', 'my tasks']):
            # Import here to avoid circular imports
            from src.api.v1.tasks import get_tasks
            user_tasks = await get_tasks(db_session, current_user_id)

            # Create a new conversation
            title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
            conversation_data = ConversationCreate(title=title_conv)
            conversation = await conversation_service.create_conversation(
                db_session, current_user_id, conversation_data
            )

            # Add the initial message to the conversation
            user_message = await conversation_service.add_message_to_conversation(
                db_session,
                conversation.id,
                current_user_id,
                request_data.content,
                "user"
            )

            # Format the tasks for the response
            if user_tasks:
                task_list = "\n".join([f"- {task.title} {'(Completed)' if task.completed else '(Pending)'}" for task in user_tasks])
                response_content = f"Here are your tasks:\n{task_list}"
            else:
                response_content = "You don't have any tasks yet."

            # Create AI response message
            ai_message = Message(
                conversation_id=conversation.id,
                user_id=current_user_id,
                role=MessageRole.assistant,
                content=response_content,
                created_at=datetime.utcnow()
            )
            db_session.add(ai_message)
            db_session.commit()
            db_session.refresh(ai_message)

            logger.info(f"User {current_user_id} initiated conversation {conversation.id} and listed tasks")

            return {
                "conversation_id": str(conversation.id),
                "user_message": MessageRead(
                    conversation_id=user_message.conversation_id,
                    user_id=user_message.user_id,
                    role=user_message.role,
                    content=user_message.content,
                    id=user_message.id,
                    created_at=user_message.created_at
                ),
                "ai_response": {
                    "id": str(ai_message.id),
                    "role": ai_message.role,
                    "content": ai_message.content,
                    "created_at": ai_message.created_at
                },
                "updated_tasks": user_tasks  # Include updated task list
            }

        # Check for task update
        elif any(keyword in content_lower for keyword in ['update task', 'change task', 'modify task']):
            # Extract task identifier and new values from the request
            import re
            task_match = re.search(r'(?:update|change|modify)\s+task\s+(\w+)(?:\s+to\s+(.*?))?(?:\s+and\s+(.*?))?', message_data.content, re.IGNORECASE)
            if task_match:
                task_identifier = task_match.group(1)
                update_values_str = task_match.group(2) or ""

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, update_task
                from src.models.task import TaskUpdate

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Parse the update values
                    update_fields = {}
                    if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                        update_fields['completed'] = True
                    elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                        update_fields['completed'] = False
                    elif 'title' in update_values_str.lower():
                        # Extract new title
                        title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if title_match:
                            update_fields['title'] = title_match.group(1).strip()
                    elif 'description' in update_values_str.lower():
                        # Extract new description
                        desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if desc_match:
                            update_fields['description'] = desc_match.group(1).strip()

                    # Create update object
                    task_update = TaskUpdate(**update_fields)
                    updated_task = await update_task(task_identifier, task_update, db_session, current_user_id)

                    # Add user message to conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conv_id,
                        current_user_id,
                        message_data.content,
                        MessageRole.user
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conv_id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've updated the task '{updated_task.title}' for you successfully!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)

                    # Update conversation's updated_at timestamp
                    try:
                        conversation = await conversation_service.get_conversation_by_id(
                            db_session, conv_id, current_user_id
                        )
                        if conversation:
                            conversation.updated_at = datetime.utcnow()
                            db_session.add(conversation)
                    except Exception as e:
                        logger.warning(f"Could not update conversation timestamp: {str(e)}")
                        # Continue anyway, this is not critical

                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} added message to conversation {conversation_id} and updated task {updated_task.id}")

                    return {
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Parse the update values
                        update_fields = {}
                        if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                            update_fields['completed'] = True
                        elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                            update_fields['completed'] = False
                        elif 'title' in update_values_str.lower():
                            # Extract new title
                            title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if title_match:
                                update_fields['title'] = title_match.group(1).strip()
                        elif 'description' in update_values_str.lower():
                            # Extract new description
                            desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if desc_match:
                                update_fields['description'] = desc_match.group(1).strip()

                        # Create update object
                        from src.models.task import TaskUpdate
                        task_update = TaskUpdate(**update_fields)
                        updated_task = await update_task(str(matching_task.id), task_update, db_session, current_user_id)

                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Get updated task list
                        from src.api.v1.tasks import get_tasks
                        updated_tasks = await get_tasks(db_session, current_user_id)

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've updated the task '{updated_task.title}' for you successfully!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} and updated task {updated_task.id}")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            },
                            "updated_tasks": updated_tasks  # Include updated task list
                        }
                    else:
                        # Task not found
                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} but task {task_identifier} not found")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # Check for task completion
        elif any(keyword in content_lower for keyword in ['complete task', 'finish task', 'done task', 'mark task']):
            # Extract task identifier from the request
            task_id_match = re.search(r'(?:complete|finish|done|mark)\s+task\s+(\w+)', request_data.content, re.IGNORECASE)
            if task_id_match:
                task_identifier = task_id_match.group(1)

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, update_task
                from src.models.task import TaskUpdate

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Update the task to mark as completed
                    task_update = TaskUpdate(completed=True)
                    updated_task = await update_task(task_identifier, task_update, db_session, current_user_id)

                    # Create a new conversation
                    title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                    conversation_data = ConversationCreate(title=title_conv)
                    conversation = await conversation_service.create_conversation(
                        db_session, current_user_id, conversation_data
                    )

                    # Add the initial message to the conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conversation.id,
                        current_user_id,
                        request_data.content,
                        "user"
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conversation.id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've marked the task '{updated_task.title}' as completed!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)
                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} initiated conversation {conversation.id} and completed task {updated_task.id}")

                    return {
                        "conversation_id": str(conversation.id),
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Update the task to mark as completed
                        from src.models.task import TaskUpdate
                        task_update = TaskUpdate(completed=True)
                        updated_task = await update_task(str(matching_task.id), task_update, db_session, current_user_id)

                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've marked the task '{updated_task.title}' as completed!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} and completed task {updated_task.id}")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }
                    else:
                        # Task not found
                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} but task {task_identifier} not found")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # Check for task update
        elif any(keyword in content_lower for keyword in ['update task', 'change task', 'modify task']):
            # Extract task identifier and new values from the request
            import re
            task_match = re.search(r'(?:update|change|modify)\s+task\s+(\w+)(?:\s+to\s+(.*?))?(?:\s+and\s+(.*?))?', request_data.content, re.IGNORECASE)
            if task_match:
                task_identifier = task_match.group(1)
                update_values_str = task_match.group(2) or ""

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, update_task
                from src.models.task import TaskUpdate

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Parse the update values
                    update_fields = {}
                    if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                        update_fields['completed'] = True
                    elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                        update_fields['completed'] = False
                    elif 'title' in update_values_str.lower():
                        # Extract new title
                        title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if title_match:
                            update_fields['title'] = title_match.group(1).strip()
                    elif 'description' in update_values_str.lower():
                        # Extract new description
                        desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if desc_match:
                            update_fields['description'] = desc_match.group(1).strip()

                    # Create update object
                    task_update = TaskUpdate(**update_fields)
                    updated_task = await update_task(task_identifier, task_update, db_session, current_user_id)

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create a new conversation
                    title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                    conversation_data = ConversationCreate(title=title_conv)
                    conversation = await conversation_service.create_conversation(
                        db_session, current_user_id, conversation_data
                    )

                    # Add the initial message to the conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conversation.id,
                        current_user_id,
                        request_data.content,
                        "user"
                    )

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conversation.id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've updated the task '{updated_task.title}' for you successfully!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)
                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} initiated conversation {conversation.id} and updated task {updated_task.id}")

                    return {
                        "conversation_id": str(conversation.id),
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Parse the update values
                        update_fields = {}
                        if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                            update_fields['completed'] = True
                        elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                            update_fields['completed'] = False
                        elif 'title' in update_values_str.lower():
                            # Extract new title
                            title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if title_match:
                                update_fields['title'] = title_match.group(1).strip()
                        elif 'description' in update_values_str.lower():
                            # Extract new description
                            desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if desc_match:
                                update_fields['description'] = desc_match.group(1).strip()

                        # Create update object
                        from src.models.task import TaskUpdate
                        task_update = TaskUpdate(**update_fields)
                        updated_task = await update_task(str(matching_task.id), task_update, db_session, current_user_id)

                        # Get updated task list
                        from src.api.v1.tasks import get_tasks
                        updated_tasks = await get_tasks(db_session, current_user_id)

                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've updated the task '{updated_task.title}' for you successfully!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} and updated task {updated_task.id}")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            },
                            "updated_tasks": updated_tasks  # Include updated task list
                        }
                    else:
                        # Task not found
                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} but task {task_identifier} not found")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # Check for task deletion
        elif any(keyword in content_lower for keyword in ['delete task', 'remove task']):
            # Extract task identifier from the request
            task_id_match = re.search(r'(?:delete|remove)\s+task\s+(\w+)', request_data.content, re.IGNORECASE)
            if task_id_match:
                task_identifier = task_id_match.group(1)

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, delete_task

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Delete the task
                    await delete_task(task_identifier, db_session, current_user_id)

                    # Create a new conversation
                    title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                    conversation_data = ConversationCreate(title=title_conv)
                    conversation = await conversation_service.create_conversation(
                        db_session, current_user_id, conversation_data
                    )

                    # Add the initial message to the conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conversation.id,
                        current_user_id,
                        request_data.content,
                        "user"
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conversation.id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've deleted the task '{task.title}' successfully!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)
                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} initiated conversation {conversation.id} and deleted task {task.id}")

                    return {
                        "conversation_id": str(conversation.id),
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Delete the task
                        await delete_task(str(matching_task.id), db_session, current_user_id)

                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've deleted the task '{matching_task.title}' successfully!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} and deleted task {matching_task.id}")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }
                    else:
                        # Task not found
                        # Create a new conversation
                        title_conv = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
                        conversation_data = ConversationCreate(title=title_conv)
                        conversation = await conversation_service.create_conversation(
                            db_session, current_user_id, conversation_data
                        )

                        # Add the initial message to the conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conversation.id,
                            current_user_id,
                            request_data.content,
                            "user"
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conversation.id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)
                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} initiated conversation {conversation.id} but task {task_identifier} not found")

                        return {
                            "conversation_id": str(conversation.id),
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # For other requests, create a new conversation normally
        title = request_data.content[:50] + "..." if len(request_data.content) > 50 else request_data.content
        conversation_data = ConversationCreate(title=title)
        conversation = await conversation_service.create_conversation(
            db_session, current_user_id, conversation_data
        )

        # Add the initial message to the conversation
        user_message = await conversation_service.add_message_to_conversation(
            db_session,
            conversation.id,
            current_user_id,
            request_data.content,
            "user"
        )

        # Initialize Cohere client
        cohere_client = cohere.Client(settings.COHERE_API_KEY)

        # Generate AI response using Cohere
        try:
            response = cohere_client.chat(
                message=request_data.content,
                preamble="You are an AI assistant helping users manage their tasks. Respond to their queries about tasks, help them create tasks, update tasks, or provide other assistance related to task management."
            )

            ai_response_content = response.text
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            ai_response_content = "Hello! I'm your AI assistant. How can I help you manage your tasks?"

        # Create AI response message
        ai_message = Message(
            conversation_id=conversation.id,
            user_id=current_user_id,  # AI responses are associated with the user for consistency
            role=MessageRole.assistant,
            content=ai_response_content,
            created_at=datetime.utcnow()
        )
        db_session.add(ai_message)
        db_session.commit()
        db_session.refresh(ai_message)

        logger.info(f"User {current_user_id} initiated conversation {conversation.id}")
        logger.info(f"AI responded to conversation {conversation.id}")

        # Get updated task list for consistency
        from src.api.v1.tasks import get_tasks
        updated_tasks = await get_tasks(db_session, current_user_id)

        return {
            "conversation_id": str(conversation.id),
            "user_message": MessageRead(
                conversation_id=user_message.conversation_id,
                user_id=user_message.user_id,
                role=user_message.role,
                content=user_message.content,
                id=user_message.id,
                created_at=user_message.created_at
            ),
            "ai_response": {
                "id": str(ai_message.id),
                "role": ai_message.role,
                "content": ai_message.content,
                "created_at": ai_message.created_at
            },
            "updated_tasks": updated_tasks  # Include updated task list for consistency
        }
    except Exception as e:
        logger.error(f"Error initiating conversation for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error initiating conversation: {str(e)}"
        )


@router.post("/conversations/{conversation_id}/messages", response_model=dict)
async def add_message_to_conversation(
    conversation_id: str,
    message_data: AddMessageRequest,
    current_user_id: uuid.UUID = CurrentUser,
    db_session: Session = Depends(get_db_session)
):
    """
    Add a message to a conversation and get AI response
    """
    try:
        conv_id = uuid.UUID(conversation_id)

        # Verify user owns the conversation
        from src.api.deps import verify_user_owns_conversation
        if not verify_user_owns_conversation(db_session, conversation_id, current_user_id):
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Access denied: You don't have permission to access this conversation"
            )

        # Verify conversation exists and belongs to user
        conversation = await conversation_service.get_conversation_by_id(
            db_session, conv_id, current_user_id
        )

        if not conversation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conversation not found"
            )

        # Check if the user wants to perform a task operation
        content_lower = message_data.content.lower()

        # Check for task operations
        import re

        # Check for task creation
        if any(keyword in content_lower for keyword in ['add task', 'create task', 'new task']):
            # Extract task information from the request
            task_match = re.search(r'(?:add task|create task|new task)[:\-]?\s*(.+?)(?:\s+with\s+description\s+(.+?))?(?=\s+[.!?]|$)', message_data.content, re.IGNORECASE)

            if task_match:
                title = task_match.group(1).strip()
                description = task_match.group(2).strip() if task_match.group(2) else None

                # Create the task
                task_data = TaskCreate(
                    title=title,
                    description=description,
                    completed=False
                )

                # Import here to avoid circular imports
                from src.api.v1.tasks import create_task
                created_task = await create_task(task_data, db_session, current_user_id)

                # Add user message to conversation
                user_message = await conversation_service.add_message_to_conversation(
                    db_session,
                    conv_id,
                    current_user_id,
                    message_data.content,
                    MessageRole.user
                )

                # Get updated task list
                from src.api.v1.tasks import get_tasks
                updated_tasks = await get_tasks(db_session, current_user_id)

                # Create AI response message
                ai_message = Message(
                    conversation_id=conv_id,
                    user_id=current_user_id,
                    role=MessageRole.assistant,
                    content=f"I've created the task '{created_task.title}' for you successfully!",
                    created_at=datetime.utcnow()
                )
                db_session.add(ai_message)

                # Update conversation's updated_at timestamp
                try:
                    conversation = await conversation_service.get_conversation_by_id(
                        db_session, conv_id, current_user_id
                    )
                    if conversation:
                        conversation.updated_at = datetime.utcnow()
                        db_session.add(conversation)
                except Exception as e:
                    logger.warning(f"Could not update conversation timestamp: {str(e)}")
                    # Continue anyway, this is not critical

                db_session.commit()
                db_session.refresh(ai_message)

                logger.info(f"User {current_user_id} added message to conversation {conversation_id} and created task {created_task.id}")

                return {
                    "user_message": MessageRead(
                        conversation_id=user_message.conversation_id,
                        user_id=user_message.user_id,
                        role=user_message.role,
                        content=user_message.content,
                        id=user_message.id,
                        created_at=user_message.created_at
                    ),
                    "ai_response": {
                        "id": str(ai_message.id),
                        "role": ai_message.role,
                        "content": ai_message.content,
                        "created_at": ai_message.created_at
                    },
                    "updated_tasks": updated_tasks  # Include updated task list
                }

        # Check for listing tasks
        elif any(keyword in content_lower for keyword in ['show my tasks', 'list tasks', 'view tasks', 'my tasks']):
            # Import here to avoid circular imports
            from src.api.v1.tasks import get_tasks
            user_tasks = await get_tasks(db_session, current_user_id)

            # Add user message to conversation
            user_message = await conversation_service.add_message_to_conversation(
                db_session,
                conv_id,
                current_user_id,
                message_data.content,
                MessageRole.user
            )

            # Format the tasks for the response
            if user_tasks:
                task_list = "\n".join([f"- {task.title} {'(Completed)' if task.completed else '(Pending)'}" for task in user_tasks])
                response_content = f"Here are your tasks:\n{task_list}"
            else:
                response_content = "You don't have any tasks yet."

            # Create AI response message
            ai_message = Message(
                conversation_id=conv_id,
                user_id=current_user_id,
                role=MessageRole.assistant,
                content=response_content,
                created_at=datetime.utcnow()
            )
            db_session.add(ai_message)

            # Update conversation's updated_at timestamp
            try:
                conversation = await conversation_service.get_conversation_by_id(
                    db_session, conv_id, current_user_id
                )
                if conversation:
                    conversation.updated_at = datetime.utcnow()
                    db_session.add(conversation)
            except Exception as e:
                logger.warning(f"Could not update conversation timestamp: {str(e)}")
                # Continue anyway, this is not critical

            db_session.commit()
            db_session.refresh(ai_message)

            logger.info(f"User {current_user_id} added message to conversation {conversation_id} and listed tasks")

            return {
                "user_message": MessageRead(
                    conversation_id=user_message.conversation_id,
                    user_id=user_message.user_id,
                    role=user_message.role,
                    content=user_message.content,
                    id=user_message.id,
                    created_at=user_message.created_at
                ),
                "ai_response": {
                    "id": str(ai_message.id),
                    "role": ai_message.role,
                    "content": ai_message.content,
                    "created_at": ai_message.created_at
                },
                "updated_tasks": user_tasks  # Include updated task list
            }

        # Check for task update
        elif any(keyword in content_lower for keyword in ['update task', 'change task', 'modify task']):
            # Extract task identifier and new values from the request
            import re
            task_match = re.search(r'(?:update|change|modify)\s+task\s+(\w+)(?:\s+to\s+(.*?))?(?:\s+and\s+(.*?))?', message_data.content, re.IGNORECASE)
            if task_match:
                task_identifier = task_match.group(1)
                update_values_str = task_match.group(2) or ""

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, update_task
                from src.models.task import TaskUpdate

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Parse the update values
                    update_fields = {}
                    if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                        update_fields['completed'] = True
                    elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                        update_fields['completed'] = False
                    elif 'title' in update_values_str.lower():
                        # Extract new title
                        title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if title_match:
                            update_fields['title'] = title_match.group(1).strip()
                    elif 'description' in update_values_str.lower():
                        # Extract new description
                        desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                        if desc_match:
                            update_fields['description'] = desc_match.group(1).strip()

                    # Create update object
                    task_update = TaskUpdate(**update_fields)
                    updated_task = await update_task(task_identifier, task_update, db_session, current_user_id)

                    # Add user message to conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conv_id,
                        current_user_id,
                        message_data.content,
                        MessageRole.user
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conv_id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've updated the task '{updated_task.title}' for you successfully!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)

                    # Update conversation's updated_at timestamp
                    try:
                        conversation = await conversation_service.get_conversation_by_id(
                            db_session, conv_id, current_user_id
                        )
                        if conversation:
                            conversation.updated_at = datetime.utcnow()
                            db_session.add(conversation)
                    except Exception as e:
                        logger.warning(f"Could not update conversation timestamp: {str(e)}")
                        # Continue anyway, this is not critical

                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} added message to conversation {conversation_id} and updated task {updated_task.id}")

                    return {
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Parse the update values
                        update_fields = {}
                        if 'complete' in update_values_str.lower() or 'done' in update_values_str.lower():
                            update_fields['completed'] = True
                        elif 'incomplete' in update_values_str.lower() or 'pending' in update_values_str.lower():
                            update_fields['completed'] = False
                        elif 'title' in update_values_str.lower():
                            # Extract new title
                            title_match = re.search(r'title\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if title_match:
                                update_fields['title'] = title_match.group(1).strip()
                        elif 'description' in update_values_str.lower():
                            # Extract new description
                            desc_match = re.search(r'description\s+to\s+(.+?)(?:\s|$)', update_values_str, re.IGNORECASE)
                            if desc_match:
                                update_fields['description'] = desc_match.group(1).strip()

                        # Create update object
                        from src.models.task import TaskUpdate
                        task_update = TaskUpdate(**update_fields)
                        updated_task = await update_task(str(matching_task.id), task_update, db_session, current_user_id)

                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Get updated task list
                        from src.api.v1.tasks import get_tasks
                        updated_tasks = await get_tasks(db_session, current_user_id)

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've updated the task '{updated_task.title}' for you successfully!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} and updated task {updated_task.id}")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            },
                            "updated_tasks": updated_tasks  # Include updated task list
                        }
                    else:
                        # Task not found
                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} but task {task_identifier} not found")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # Check for task completion
        elif any(keyword in content_lower for keyword in ['complete task', 'finish task', 'done task', 'mark task']):
            # Extract task identifier from the request
            task_id_match = re.search(r'(?:complete|finish|done|mark)\s+task\s+(\w+)', message_data.content, re.IGNORECASE)
            if task_id_match:
                task_identifier = task_id_match.group(1)

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, update_task
                from src.models.task import TaskUpdate

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Update the task to mark as completed
                    task_update = TaskUpdate(completed=True)
                    updated_task = await update_task(task_identifier, task_update, db_session, current_user_id)

                    # Add user message to conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conv_id,
                        current_user_id,
                        message_data.content,
                        MessageRole.user
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conv_id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've marked the task '{updated_task.title}' as completed!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)

                    # Update conversation's updated_at timestamp
                    try:
                        conversation = await conversation_service.get_conversation_by_id(
                            db_session, conv_id, current_user_id
                        )
                        if conversation:
                            conversation.updated_at = datetime.utcnow()
                            db_session.add(conversation)
                    except Exception as e:
                        logger.warning(f"Could not update conversation timestamp: {str(e)}")
                        # Continue anyway, this is not critical

                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} added message to conversation {conversation_id} and completed task {updated_task.id}")

                    return {
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Update the task to mark as completed
                        from src.models.task import TaskUpdate
                        task_update = TaskUpdate(completed=True)
                        updated_task = await update_task(str(matching_task.id), task_update, db_session, current_user_id)

                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've marked the task '{updated_task.title}' as completed!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} and completed task {updated_task.id}")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }
                    else:
                        # Task not found
                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} but task {task_identifier} not found")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # Check for task deletion
        elif any(keyword in content_lower for keyword in ['delete task', 'remove task']):
            # Extract task identifier from the request
            task_id_match = re.search(r'(?:delete|remove)\s+task\s+(\w+)', message_data.content, re.IGNORECASE)
            if task_id_match:
                task_identifier = task_id_match.group(1)

                # Import here to avoid circular imports
                from src.api.v1.tasks import get_task, delete_task

                try:
                    # First, try to get the task by ID if it's a valid UUID
                    task = await get_task(task_identifier, db_session, current_user_id)

                    # Delete the task
                    await delete_task(task_identifier, db_session, current_user_id)

                    # Add user message to conversation
                    user_message = await conversation_service.add_message_to_conversation(
                        db_session,
                        conv_id,
                        current_user_id,
                        message_data.content,
                        MessageRole.user
                    )

                    # Get updated task list
                    from src.api.v1.tasks import get_tasks
                    updated_tasks = await get_tasks(db_session, current_user_id)

                    # Create AI response message
                    ai_message = Message(
                        conversation_id=conv_id,
                        user_id=current_user_id,
                        role=MessageRole.assistant,
                        content=f"I've deleted the task '{task.title}' successfully!",
                        created_at=datetime.utcnow()
                    )
                    db_session.add(ai_message)

                    # Update conversation's updated_at timestamp
                    try:
                        conversation = await conversation_service.get_conversation_by_id(
                            db_session, conv_id, current_user_id
                        )
                        if conversation:
                            conversation.updated_at = datetime.utcnow()
                            db_session.add(conversation)
                    except Exception as e:
                        logger.warning(f"Could not update conversation timestamp: {str(e)}")
                        # Continue anyway, this is not critical

                    db_session.commit()
                    db_session.refresh(ai_message)

                    logger.info(f"User {current_user_id} added message to conversation {conversation_id} and deleted task {task.id}")

                    return {
                        "user_message": MessageRead(
                            conversation_id=user_message.conversation_id,
                            user_id=user_message.user_id,
                            role=user_message.role,
                            content=user_message.content,
                            id=user_message.id,
                            created_at=user_message.created_at
                        ),
                        "ai_response": {
                            "id": str(ai_message.id),
                            "role": ai_message.role,
                            "content": ai_message.content,
                            "created_at": ai_message.created_at
                        },
                        "updated_tasks": updated_tasks  # Include updated task list
                    }
                except HTTPException:
                    # If the task wasn't found by ID, try to find by title
                    from src.api.v1.tasks import get_tasks
                    user_tasks = await get_tasks(db_session, current_user_id)

                    # Find task by title
                    matching_task = None
                    for task in user_tasks:
                        if task_identifier.lower() in task.title.lower():
                            matching_task = task
                            break

                    if matching_task:
                        # Delete the task
                        await delete_task(str(matching_task.id), db_session, current_user_id)

                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"I've deleted the task '{matching_task.title}' successfully!",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} and deleted task {matching_task.id}")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }
                    else:
                        # Task not found
                        # Add user message to conversation
                        user_message = await conversation_service.add_message_to_conversation(
                            db_session,
                            conv_id,
                            current_user_id,
                            message_data.content,
                            MessageRole.user
                        )

                        # Create AI response message
                        ai_message = Message(
                            conversation_id=conv_id,
                            user_id=current_user_id,
                            role=MessageRole.assistant,
                            content=f"Sorry, I couldn't find a task with ID or title '{task_identifier}'.",
                            created_at=datetime.utcnow()
                        )
                        db_session.add(ai_message)

                        # Update conversation's updated_at timestamp
                        try:
                            conversation = await conversation_service.get_conversation_by_id(
                                db_session, conv_id, current_user_id
                            )
                            if conversation:
                                conversation.updated_at = datetime.utcnow()
                                db_session.add(conversation)
                        except Exception as e:
                            logger.warning(f"Could not update conversation timestamp: {str(e)}")
                            # Continue anyway, this is not critical

                        db_session.commit()
                        db_session.refresh(ai_message)

                        logger.info(f"User {current_user_id} added message to conversation {conversation_id} but task {task_identifier} not found")

                        return {
                            "user_message": MessageRead(
                                conversation_id=user_message.conversation_id,
                                user_id=user_message.user_id,
                                role=user_message.role,
                                content=user_message.content,
                                id=user_message.id,
                                created_at=user_message.created_at
                            ),
                            "ai_response": {
                                "id": str(ai_message.id),
                                "role": ai_message.role,
                                "content": ai_message.content,
                                "created_at": ai_message.created_at
                            }
                        }

        # For other requests, proceed with normal conversation flow
        # Add user message to conversation
        user_message = await conversation_service.add_message_to_conversation(
            db_session,
            conv_id,
            current_user_id,
            message_data.content,
            MessageRole.user  # Use the enum value instead of string
        )

        # Initialize Cohere client
        cohere_client = cohere.Client(settings.COHERE_API_KEY)

        # Get all messages in the conversation for context
        all_messages = await conversation_service.get_messages_for_conversation(
            db_session, conv_id, current_user_id
        )

        # Format messages for the AI
        chat_history = []
        for msg in all_messages:
            role = "USER" if msg.role == MessageRole.user else "CHATBOT"
            chat_history.append({
                "role": role,
                "message": msg.content
            })

        # Generate AI response using Cohere
        try:
            response = cohere_client.chat(
                message=message_data.content,
                chat_history=chat_history[:-1],  # Exclude the current message from history
                preamble="You are an AI assistant helping users manage their tasks. Respond to their queries about tasks, help them create tasks, update tasks, or provide other assistance related to task management."
            )

            ai_response_content = response.text
        except Exception as e:
            logger.error(f"Error generating AI response: {str(e)}")
            ai_response_content = "I'm sorry, I encountered an error processing your request. Could you please try again?"

        # Create AI response message
        ai_message = Message(
            conversation_id=conv_id,
            user_id=current_user_id,  # AI responses are associated with the user for consistency
            role=MessageRole.assistant,
            content=ai_response_content,
            created_at=datetime.utcnow()
        )
        db_session.add(ai_message)

        # Update conversation's updated_at timestamp
        try:
            conversation = await conversation_service.get_conversation_by_id(
                db_session, conv_id, current_user_id
            )
            if conversation:
                conversation.updated_at = datetime.utcnow()
                db_session.add(conversation)
        except Exception as e:
            logger.warning(f"Could not update conversation timestamp: {str(e)}")
            # Continue anyway, this is not critical

        db_session.commit()
        db_session.refresh(ai_message)

        logger.info(f"User {current_user_id} added message to conversation {conversation_id}")
        logger.info(f"AI responded to conversation {conversation_id}")

        # Get updated task list for consistency
        from src.api.v1.tasks import get_tasks
        updated_tasks = await get_tasks(db_session, current_user_id)

        return {
            "user_message": MessageRead(
                conversation_id=user_message.conversation_id,
                user_id=user_message.user_id,
                role=user_message.role,
                content=user_message.content,
                id=user_message.id,
                created_at=user_message.created_at
            ),
            "ai_response": {
                "id": str(ai_message.id),
                "role": ai_message.role,
                "content": ai_message.content,
                "created_at": ai_message.created_at
            },
            "updated_tasks": updated_tasks  # Include updated task list for consistency
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error adding message to conversation {conversation_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error adding message to conversation: {str(e)}"
        )