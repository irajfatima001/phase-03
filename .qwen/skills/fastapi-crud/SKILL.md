# Skill: fastapi-crud

**Name**: fastapi-crud  
**Description**: Generates standard REST CRUD endpoints in FastAPI with /api/{user_id}/tasks prefix and strict user isolation

## Purpose
This skill generates standard REST CRUD endpoints in FastAPI with strict user isolation. It ensures that users can only access, modify, or delete resources that belong to them, using the /api/{user_id}/tasks endpoint pattern.

## Allowed Tools
- code_write

## Implementation Instructions

### 1. Pydantic Models
```python
# src/models/task.py
from sqlmodel import SQLModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"

class TaskPriority(str, Enum):
    low = "low"
    medium = "medium"
    high = "high"

class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=1000)
    status: TaskStatus = Field(default=TaskStatus.pending)
    priority: TaskPriority = Field(default=TaskPriority.medium)
    user_id: str = Field(foreign_key="user.id")

class Task(TaskBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    updated_at: Optional[datetime] = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = Field(default=None)

class TaskRead(TaskBase):
    id: int
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime]

class TaskUpdate(SQLModel):
    title: Optional[str] = None
    description: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[TaskPriority] = None

class TaskComplete(SQLModel):
    complete: bool
```

### 2. API Router Setup
```python
# src/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from ..database.session import get_db_session
from ..models.task import Task, TaskRead, TaskUpdate, TaskComplete
from ..models.user import UserToken
from ..api.deps import get_current_user
from ..services.task_service import (
    get_tasks_by_user_id,
    create_task_for_user_id,
    get_task_by_id_and_user_id,
    update_task_by_id_and_user_id,
    delete_task_by_id_and_user_id,
    update_task_completion_status
)

router = APIRouter(prefix="/api/{user_id}/tasks", tags=["tasks"])
```

### 3. GET List Endpoint
```python
@router.get("/", response_model=List[TaskRead])
async def get_tasks(
    user_id: str,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100
):
    """
    Get all tasks for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    tasks = await get_tasks_by_user_id(session, user_id, skip, limit)
    return tasks
```

### 4. POST Create Endpoint
```python
@router.post("/", response_model=TaskRead, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task: Task,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Create a new task for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    # Ensure the task is associated with the correct user
    task.user_id = user_id
    
    created_task = await create_task_for_user_id(session, task)
    return created_task
```

### 5. GET by ID Endpoint
```python
@router.get("/{task_id}", response_model=TaskRead)
async def get_task(
    user_id: str,
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Get a specific task by ID for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    task = await get_task_by_id_and_user_id(session, task_id, user_id)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return task
```

### 6. PUT Update Endpoint
```python
@router.put("/{task_id}", response_model=TaskRead)
async def update_task(
    user_id: str,
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Update a specific task by ID for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    updated_task = await update_task_by_id_and_user_id(
        session, task_id, user_id, task_update
    )
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return updated_task
```

### 7. DELETE Endpoint
```python
@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Delete a specific task by ID for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    success = await delete_task_by_id_and_user_id(session, task_id, user_id)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return
```

### 8. PATCH Complete Endpoint
```python
@router.patch("/{task_id}/complete", response_model=TaskRead)
async def update_task_complete(
    user_id: str,
    task_id: int,
    task_complete: TaskComplete,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """
    Mark a specific task as complete/incomplete for a specific user
    """
    # Verify that the requested user_id matches the authenticated user
    if user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Access forbidden: user_id mismatch"
        )
    
    updated_task = await update_task_completion_status(
        session, task_id, user_id, task_complete
    )
    
    if not updated_task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )
    
    return updated_task
```

### 9. Service Layer Implementation
```python
# src/services/task_service.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import List
from ..models.task import Task, TaskUpdate, TaskComplete, TaskStatus

async def get_tasks_by_user_id(
    session: AsyncSession, 
    user_id: str, 
    skip: int = 0, 
    limit: int = 100
) -> List[Task]:
    """Get all tasks for a specific user"""
    statement = select(Task).where(Task.user_id == user_id).offset(skip).limit(limit)
    result = await session.execute(statement)
    return result.scalars().all()

async def create_task_for_user_id(session: AsyncSession, task: Task) -> Task:
    """Create a new task for a specific user"""
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_task_by_id_and_user_id(
    session: AsyncSession, 
    task_id: int, 
    user_id: str
) -> Task:
    """Get a specific task by ID for a specific user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update_task_by_id_and_user_id(
    session: AsyncSession, 
    task_id: int, 
    user_id: str, 
    task_update: TaskUpdate
) -> Task:
    """Update a specific task by ID for a specific user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    if not task:
        return None
    
    # Update fields that are provided
    update_data = task_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(task, field, value)
    
    await session.commit()
    await session.refresh(task)
    return task

async def delete_task_by_id_and_user_id(
    session: AsyncSession, 
    task_id: int, 
    user_id: str
) -> bool:
    """Delete a specific task by ID for a specific user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    if not task:
        return False
    
    await session.delete(task)
    await session.commit()
    return True

async def update_task_completion_status(
    session: AsyncSession, 
    task_id: int, 
    user_id: str, 
    task_complete: TaskComplete
) -> Task:
    """Update the completion status of a specific task for a specific user"""
    statement = select(Task).where(Task.id == task_id, Task.user_id == user_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    if not task:
        return None
    
    # Update status based on completion request
    if task_complete.complete:
        task.status = TaskStatus.completed
        task.completed_at = datetime.utcnow()
    else:
        task.status = TaskStatus.pending
        task.completed_at = None
    
    await session.commit()
    await session.refresh(task)
    return task
```

### 10. Main Application Setup
```python
# main.py
from fastapi import FastAPI
from contextlib import asynccontextmanager
from sqlmodel import SQLModel
from .src.database.session import engine
from .src.api.tasks import router as tasks_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Cleanup on shutdown
    await engine.dispose()

app = FastAPI(lifespan=lifespan)

# Include the tasks router
app.include_router(tasks_router)
```

## Key Features
- Standard REST CRUD endpoints with proper HTTP status codes
- Strict user isolation with user_id validation in both URL and token
- Uses APIRouter with /api/{user_id}/tasks prefix
- Implements authentication with Depends(get_current_user)
- Filters all queries by user_id to prevent data leakage
- Uses SQLModel for database operations
- Includes Pydantic models for request/response validation
- Proper error handling with appropriate HTTP status codes

## Security Considerations
- Always validate that the user_id in the URL matches the authenticated user
- Filter all database queries by user_id to prevent unauthorized access
- Use HTTP 403 Forbidden for user_id mismatches
- Use HTTP 404 Not Found for non-existent resources
- Implement proper authentication with JWT tokens
- Never expose other users' data through the API

## Best Practices
- Use consistent endpoint patterns across the API
- Implement proper request/response validation
- Use appropriate HTTP status codes
- Follow REST conventions for endpoint design
- Separate concerns with service layer functions
- Use dependency injection for authentication
- Implement proper error handling
- Document all endpoints with OpenAPI