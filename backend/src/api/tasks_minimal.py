from fastapi import APIRouter
from typing import List
from src.models.task import Task, TaskCreate, TaskUpdate, TaskComplete, TaskStatus


router = APIRouter()


@router.post("/tasks")
async def create_task(task_data: TaskCreate):
    """
    Create a new task
    """
    # For debugging, return a simple response
    return {"id": "test-id", "title": task_data.title, "user_id": task_data.user_id}


@router.get("/{user_id}/tasks")
async def get_tasks(user_id: str):
    """
    Get all tasks for a specific user
    """
    # For debugging, return a simple response
    return []


@router.patch("/tasks/{task_id}")
async def update_task(task_id: str, task_update: TaskUpdate):
    """
    Update a specific task
    """
    # For debugging, return a simple response
    return {"id": task_id, "updated": True}


@router.delete("/tasks/{task_id}")
async def delete_task(task_id: str):
    """
    Delete a specific task
    """
    # For debugging, return a simple response
    return {"id": task_id, "deleted": True}


@router.put("/tasks/{task_id}/complete")
async def update_task_complete(task_id: str, task_complete: TaskComplete):
    """
    Mark a task as complete/incomplete
    """
    # For debugging, return a simple response
    return {"id": task_id, "completed": task_complete.complete}