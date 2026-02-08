# Skill: user-isolation-filter

**Name**: user-isolation-filter  
**Description**: Enforces user_id filtering in all SQLModel queries and raises 403 on ownership violation

## Purpose
This skill ensures that users can only access, modify, or delete resources that belong to them. It adds user_id filtering to all database queries and validates ownership before allowing operations, preventing unauthorized access to other users' data.

## Allowed Tools
- code_read
- code_edit

## Implementation Instructions

### 1. Basic Query Filtering Pattern
```python
# Add .where(Model.user_id == current_user.user_id) to all queries
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession

# Example: Get all tasks for current user only
async def get_tasks_for_user(session: AsyncSession, current_user: UserToken):
    statement = select(Task).where(Task.user_id == current_user.user_id)
    result = await session.execute(statement)
    return result.scalars().all()
```

### 2. Ownership Validation Before Updates
```python
# Before updating or deleting, verify ownership
from fastapi import HTTPException, status

async def update_task(
    session: AsyncSession, 
    task_id: int, 
    current_user: UserToken, 
    task_update: TaskUpdate
):
    # First, get the task to check ownership
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    # Check if task exists and belongs to current user
    if not task or task.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only modify your own tasks"
        )
    
    # Update the task
    for field, value in task_update.dict(exclude_unset=True).items():
        setattr(task, field, value)
    
    await session.commit()
    await session.refresh(task)
    return task
```

### 3. Ownership Validation Before Deletion
```python
async def delete_task(session: AsyncSession, task_id: int, current_user: UserToken):
    # Get the task to check ownership
    statement = select(Task).where(Task.id == task_id)
    result = await session.execute(statement)
    task = result.scalar_one_or_none()
    
    # Check if task exists and belongs to current user
    if not task or task.user_id != current_user.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="You can only delete your own tasks"
        )
    
    # Delete the task
    await session.delete(task)
    await session.commit()
    return True
```

### 4. Service Layer Implementation
```python
# src/services/task_service.py
from sqlmodel import select
from sqlmodel.ext.asyncio.session import AsyncSession
from fastapi import HTTPException, status
from ..models.task import Task, TaskUpdate
from ..models.user import UserToken

async def get_user_tasks(
    session: AsyncSession, 
    current_user: UserToken,
    skip: int = 0,
    limit: int = 100
):
    """Get all tasks belonging to the current user"""
    statement = select(Task).where(
        Task.user_id == current_user.user_id
    ).offset(skip).limit(limit)
    
    result = await session.execute(statement)
    return result.scalars().all()

async def create_task_for_user(
    session: AsyncSession, 
    task: Task, 
    current_user: UserToken
):
    """Create a task associated with the current user"""
    task.user_id = current_user.user_id
    session.add(task)
    await session.commit()
    await session.refresh(task)
    return task

async def get_task_by_id_and_user(
    session: AsyncSession, 
    task_id: int, 
    current_user: UserToken
):
    """Get a specific task if it belongs to the current user"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.user_id
    )
    
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def update_task_by_id_and_user(
    session: AsyncSession, 
    task_id: int, 
    task_update: TaskUpdate, 
    current_user: UserToken
):
    """Update a task if it belongs to the current user"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.user_id
    )
    
    result = await session.execute(statement)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task not found or access denied"
        )
    
    # Update the task with provided values
    for field, value in task_update.model_dump(exclude_unset=True).items():
        setattr(db_task, field, value)
    
    await session.commit()
    await session.refresh(db_task)
    return db_task

async def delete_task_by_id_and_user(
    session: AsyncSession, 
    task_id: int, 
    current_user: UserToken
):
    """Delete a task if it belongs to the current user"""
    statement = select(Task).where(
        Task.id == task_id,
        Task.user_id == current_user.user_id
    )
    
    result = await session.execute(statement)
    db_task = result.scalar_one_or_none()
    
    if not db_task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task not found or access denied"
        )
    
    await session.delete(db_task)
    await session.commit()
    return True
```

### 5. API Endpoint Implementation
```python
# src/api/tasks.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel.ext.asyncio.session import AsyncSession
from ..database.session import get_db_session
from ..models.task import Task, TaskUpdate
from ..models.user import UserToken
from ..api.deps import get_current_user
from ..services.task_service import (
    get_user_tasks,
    create_task_for_user,
    get_task_by_id_and_user,
    update_task_by_id_and_user,
    delete_task_by_id_and_user
)

router = APIRouter()

@router.get("/", response_model=list[Task])
async def read_tasks(
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session),
    skip: int = 0,
    limit: int = 100
):
    """Get all tasks for the current user"""
    tasks = await get_user_tasks(session, current_user, skip, limit)
    return tasks

@router.post("/", response_model=Task)
async def create_task(
    task: Task,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Create a task for the current user"""
    return await create_task_for_user(session, task, current_user)

@router.get("/{task_id}", response_model=Task)
async def read_task(
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Get a specific task if it belongs to the current user"""
    task = await get_task_by_id_and_user(session, task_id, current_user)
    if not task:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task not found or access denied"
        )
    return task

@router.put("/{task_id}", response_model=Task)
async def update_task(
    task_id: int,
    task_update: TaskUpdate,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Update a task if it belongs to the current user"""
    return await update_task_by_id_and_user(session, task_id, task_update, current_user)

@router.delete("/{task_id}")
async def delete_task(
    task_id: int,
    current_user: UserToken = Depends(get_current_user),
    session: AsyncSession = Depends(get_db_session)
):
    """Delete a task if it belongs to the current user"""
    success = await delete_task_by_id_and_user(session, task_id, current_user)
    if not success:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Task not found or access denied"
        )
    return {"message": "Task deleted successfully"}
```

### 6. Review and Audit Existing Code
```python
# Function to audit existing code for missing user isolation
def audit_queries_for_user_isolation(file_path: str):
    """
    Reviews code for potential user isolation issues
    Looks for queries that don't filter by user_id
    """
    with open(file_path, 'r') as f:
        content = f.read()
    
    # Look for patterns that might indicate missing user isolation
    import re
    
    # Find all select statements
    select_pattern = r'select\([^)]*\)'
    selects = re.findall(select_pattern, content, re.IGNORECASE)
    
    # Check if each select statement includes user_id filter
    for select_stmt in selects:
        if 'user_id' not in select_stmt.lower():
            print(f"POTENTIAL ISSUE: {select_stmt} might be missing user_id filter")
    
    # Find all update/delete operations
    update_delete_pattern = r'(update|delete).*?\..*?(where|filter)'
    updates_deletes = re.findall(update_delete_pattern, content, re.IGNORECASE)
    
    for op in updates_deletes:
        if 'user_id' not in op[1].lower():
            print(f"POTENTIAL ISSUE: Update/delete operation might be missing user_id check")
```

### 7. Common Patterns to Look For and Fix
```python
# PATTERN 1: Queries without user_id filter
# BEFORE (VULNERABLE):
# statement = select(Task).where(Task.status == "active")

# AFTER (SECURE):
# statement = select(Task).where(Task.status == "active", Task.user_id == current_user.user_id)

# PATTERN 2: Direct access without ownership check
# BEFORE (VULNERABLE):
# task = session.get(Task, task_id)

# AFTER (SECURE):
# statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.user_id)
# result = await session.execute(statement)
# task = result.scalar_one_or_none()

# PATTERN 3: Updates without ownership validation
# BEFORE (VULNERABLE):
# task = session.get(Task, task_id)
# task.title = new_title

# AFTER (SECURE):
# statement = select(Task).where(Task.id == task_id, Task.user_id == current_user.user_id)
# result = await session.execute(statement)
# task = result.scalar_one_or_none()
# if not task:
#     raise HTTPException(status_code=403, detail="Access denied")
# task.title = new_title
```

## Key Features
- Enforces user_id filtering in all database queries
- Validates ownership before allowing updates or deletions
- Raises HTTP 403 Forbidden on ownership violations
- Provides patterns for secure query construction
- Includes audit functions to identify potential vulnerabilities
- Works with SQLModel and async sessions
- Integrates with FastAPI dependency system

## Security Considerations
- Always filter queries by user_id to prevent unauthorized access
- Validate ownership before allowing modifications
- Use HTTP 403 status code for access violations
- Never trust client-provided IDs without server-side validation
- Implement consistent isolation across all endpoints
- Regularly audit code for missing isolation filters
- Use parameterized queries to prevent SQL injection

## Best Practices
- Apply user_id filtering consistently across all queries
- Use dedicated service functions that enforce isolation
- Implement proper error handling for access violations
- Test with multiple user accounts to verify isolation
- Document the isolation requirements for the API
- Use automated tools to scan for missing isolation filters