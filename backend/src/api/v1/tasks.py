from fastapi import APIRouter, Depends, HTTPException, status
from typing import List
from sqlmodel import Session, select
from uuid import UUID
from datetime import datetime
from src.models.task import Task, TaskCreate, TaskUpdate, TaskRead
from src.api.deps import CurrentUser, get_db_session
from fastapi import Depends
from src.core.logging_config import get_logger
import uuid


router = APIRouter()
logger = get_logger(__name__)


@router.get("/tasks", response_model=List[TaskRead])
async def get_tasks(
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Get all tasks for the authenticated user
    """
    try:
        # Query tasks for the authenticated user
        statement = select(Task).where(Task.user_id == current_user_id)
        tasks = db_session.exec(statement).all()

        logger.info(f"User {current_user_id} retrieved {len(tasks)} tasks")
        return tasks
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving tasks for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving tasks: {str(e)}"
        )


@router.post("/tasks", response_model=TaskRead)
async def create_task(
    task_data: TaskCreate,
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Create a new task for the authenticated user
    """
    try:
        # Validate required fields
        if not task_data.title or task_data.title.strip() == "":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Task title is required"
            )

        # Create a new task with the authenticated user's ID
        task = Task.model_validate(
            {
                "title": task_data.title,
                "description": task_data.description,
                "completed": task_data.completed or False,
                "due_date": task_data.due_date,
                "user_id": current_user_id,
                "priority": task_data.priority or "medium"
            }
        )

        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        logger.info(f"User {current_user_id} created task {task.id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating task for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error creating task: {str(e)}"
        )


@router.get("/tasks/{task_id}", response_model=TaskRead)
async def get_task(
    task_id: str,
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Get a specific task by ID
    """
    try:
        task_uuid = uuid.UUID(task_id)

        # Get the task from the database
        task = db_session.get(Task, task_uuid)

        # Verify that the task belongs to the authenticated user
        if not task or task.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        logger.info(f"User {current_user_id} retrieved task {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving task {task_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving task: {str(e)}"
        )


@router.patch("/tasks/{task_id}", response_model=TaskRead)
async def update_task(
    task_id: str,
    task_update: TaskUpdate,
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Update a specific task by ID
    """
    try:
        task_uuid = uuid.UUID(task_id)

        # Get the task from the database
        task = db_session.get(Task, task_uuid)

        # Verify that the task belongs to the authenticated user
        if not task or task.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update the task with the provided data
        update_data = task_update.model_dump(exclude_unset=True)
        for field, value in update_data.items():
            setattr(task, field, value)

        # Update the updated_at timestamp
        task.updated_at = datetime.utcnow()
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        logger.info(f"User {current_user_id} updated task {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task {task_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task: {str(e)}"
        )


@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Delete a specific task by ID
    """
    try:
        task_uuid = uuid.UUID(task_id)

        # Get the task from the database
        task = db_session.get(Task, task_uuid)

        # Verify that the task belongs to the authenticated user
        if not task or task.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Store task info before deletion for response
        task_info = {
            "id": str(task.id),
            "title": task.title,
            "description": task.description
        }

        # Delete the task
        db_session.delete(task)
        db_session.commit()

        logger.info(f"User {current_user_id} deleted task {task_id}")
        return {"message": "Task deleted successfully", "deleted_task": task_info}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error deleting task {task_id} for user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error deleting task: {str(e)}"
        )


@router.put("/tasks/{task_id}/complete", response_model=TaskRead)
async def update_task_complete(
    task_id: str,
    task_complete: dict,  # Using dict instead of TaskComplete for simplicity
    db_session: Session = Depends(get_db_session),
    current_user_id: UUID = CurrentUser
):
    """
    Mark a task as complete/incomplete
    """
    try:
        task_uuid = uuid.UUID(task_id)

        # Get the task from the database
        task = db_session.get(Task, task_uuid)

        # Verify that the task belongs to the authenticated user
        if not task or task.user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Task not found"
            )

        # Update the task's completed status
        task.completed = task_complete.get("complete", False)
        task.updated_at = datetime.utcnow()  # Update timestamp
        db_session.add(task)
        db_session.commit()
        db_session.refresh(task)

        logger.info(f"User {current_user_id} updated completion status of task {task_id}")
        return task
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating task completion status for task {task_id}, user {current_user_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error updating task completion: {str(e)}"
        )