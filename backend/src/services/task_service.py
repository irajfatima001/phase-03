from typing import List, Optional
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from src.models.task import Task, TaskUpdate, TaskComplete, TaskStatus
from src.database.session import engine
from datetime import datetime


async def get_tasks_by_user_id(user_id: str) -> List[Task]:
    """Get all tasks for a specific user"""
    async with AsyncSession(engine) as session:
        statement = select(Task).where(Task.user_id == user_id)
        result = await session.execute(statement)
        return result.scalars().all()


async def create_task_for_user_id(user_id: str, task_data: Task) -> Task:
    """Create a new task for a specific user"""
    async with AsyncSession(engine) as session:
        # Create task with user_id
        db_task = Task(
            title=task_data.title,
            description=task_data.description,
            status=task_data.status,
            priority=task_data.priority,
            user_id=user_id
        )
        session.add(db_task)
        await session.commit()
        await session.refresh(db_task)
        return db_task


async def get_task_by_id_and_user_id(task_id: str, user_id: str) -> Optional[Task]:
    """Get a specific task by ID for a specific user"""
    async with AsyncSession(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        return result.scalar_one_or_none()


async def update_task_by_id_and_user_id(task_id: str, user_id: str, task_update: TaskUpdate) -> Optional[Task]:
    """Update a specific task by ID for a specific user"""
    async with AsyncSession(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        # Update fields that are provided
        update_data = task_update.model_dump(exclude_unset=True)  # Changed from dict() to model_dump()
        for field, value in update_data.items():
            setattr(db_task, field, value)

        db_task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(db_task)
        return db_task


async def delete_task_by_id_and_user_id(task_id: str, user_id: str) -> bool:
    """Delete a specific task by ID for a specific user"""
    async with AsyncSession(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return False

        await session.delete(db_task)
        await session.commit()
        return True


async def update_task_completion_status(task_id: str, user_id: str, task_complete: TaskComplete) -> Optional[Task]:
    """Update the completion status of a specific task for a specific user"""
    async with AsyncSession(engine) as session:
        statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
        result = await session.execute(statement)
        db_task = result.scalar_one_or_none()

        if not db_task:
            return None

        # Update status based on completion request
        if task_complete.complete:
            db_task.status = TaskStatus.completed
            db_task.completed_at = datetime.utcnow()
        else:
            db_task.status = TaskStatus.pending
            db_task.completed_at = None

        db_task.updated_at = datetime.utcnow()
        await session.commit()
        await session.refresh(db_task)
        return db_task