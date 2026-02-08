from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
from enum import Enum
import uuid
from datetime import datetime


class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"


class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"


class Task(BaseModel):
    id: str
    title: str
    description: str = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    user_id: str
    created_at: str = None
    updated_at: str = None
    completed_at: str = None


class TaskCreate(BaseModel):
    title: str
    description: str = None
    status: TaskStatus = TaskStatus.pending
    priority: TaskPriority = TaskPriority.medium
    user_id: str


class TaskUpdate(BaseModel):
    title: str = None
    description: str = None
    status: TaskStatus = None
    priority: TaskPriority = None


class TaskComplete(BaseModel):
    complete: bool


router = APIRouter()


@router.post("/tasks", response_model=Task)
async def create_task(task_data: TaskCreate):
    """
    Create a new task
    """
    task = Task(
        id=str(uuid.uuid4()),
        title=task_data.title,
        description=task_data.description,
        status=task_data.status,
        priority=task_data.priority,
        user_id=task_data.user_id,
        created_at=datetime.utcnow().isoformat()
    )
    # In a real implementation, this would save to the database
    return task


@router.get("/{user_id}/tasks", response_model=List[Task])
async def get_tasks(user_id: str):
    """
    Get all tasks for a specific user
    """
    # In a real implementation, this would fetch from the database
    # For now, return an empty list
    return []


@router.patch("/tasks/{task_id}", response_model=Task)
async def update_task(task_id: str, task_update: TaskUpdate):
    """
    Update a specific task
    """
    # In a real implementation, this would update the database
    # For now, return a mock updated task
    task = Task(
        id=task_id,
        title="Updated Task",
        description="Updated Description",
        status=task_update.status or TaskStatus.pending,
        priority=task_update.priority or TaskPriority.medium,
        user_id="mock-user-id",
        updated_at=datetime.utcnow().isoformat()
    )
    return task


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a specific task
    """
    # In a real implementation, this would delete from the database
    return {"message": "Task deleted"}


@router.put("/tasks/{task_id}/complete", response_model=Task)
async def update_task_complete(task_id: str, task_complete: TaskComplete):
    """
    Mark a task as complete/incomplete
    """
    # In a real implementation, this would update the database
    # For now, return a mock updated task
    status = TaskStatus.completed if task_complete.complete else TaskStatus.pending
    completed_at = datetime.utcnow().isoformat() if task_complete.complete else None
    
    task = Task(
        id=task_id,
        title="Mock Task",
        description="Mock Description",
        status=status,
        priority=TaskPriority.medium,
        user_id="mock-user-id",
        completed_at=completed_at,
        updated_at=datetime.utcnow().isoformat()
    )
    return task