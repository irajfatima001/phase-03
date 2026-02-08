import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.services.task_service import (
    get_tasks_by_user_id,
    create_task_for_user_id,
    get_task_by_id_and_user_id,
    update_task_by_id_and_user_id,
    delete_task_by_id_and_user_id,
    update_task_completion_status
)
from src.models.task import Task, TaskUpdate, TaskComplete, TaskStatus


@pytest.mark.asyncio
async def test_get_tasks_by_user_id():
    # Mock the database session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalars.return_value.all.return_value = [
        Task(id="1", title="Test Task", user_id="user123", status=TaskStatus.pending, priority="medium")
    ]
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    # Patch the engine context manager
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        tasks = await get_tasks_by_user_id("user123")
        
        assert len(tasks) == 1
        assert tasks[0].title == "Test Task"


@pytest.mark.asyncio
async def test_create_task_for_user_id():
    task_data = Task(title="New Task", description="Test description", user_id="user123", priority="medium")
    
    # Mock the database session
    mock_session = AsyncMock(spec=AsyncSession)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        created_task = await create_task_for_user_id("user123", task_data)
        
        # Verify that the task was added to the session
        mock_session.add.assert_called_once()
        # Verify that commit and refresh were called
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


@pytest.mark.asyncio
async def test_get_task_by_id_and_user_id_found():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_task = Task(id="1", title="Test Task", user_id="user123", status=TaskStatus.pending, priority="medium")
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        task = await get_task_by_id_and_user_id("1", "user123")
        
        assert task is not None
        assert task.id == "1"


@pytest.mark.asyncio
async def test_get_task_by_id_and_user_id_not_found():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_result.scalar_one_or_none.return_value = None
    mock_session.execute = AsyncMock(return_value=mock_result)
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        task = await get_task_by_id_and_user_id("nonexistent", "user123")
        
        assert task is None


@pytest.mark.asyncio
async def test_update_task_by_id_and_user_id():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_task = Task(id="1", title="Old Title", user_id="user123", status=TaskStatus.pending, priority="medium")
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    update_data = TaskUpdate(title="Updated Title")
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        updated_task = await update_task_by_id_and_user_id("1", "user123", update_data)
        
        assert updated_task is not None
        assert updated_task.title == "Updated Title"
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_delete_task_by_id_and_user_id():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_task = Task(id="1", title="To Delete", user_id="user123", status=TaskStatus.pending, priority="medium")
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.delete = MagicMock()
    mock_session.commit = AsyncMock()
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        result = await delete_task_by_id_and_user_id("1", "user123")
        
        assert result is True
        mock_session.delete.assert_called_once_with(mock_task)
        mock_session.commit.assert_called_once()


@pytest.mark.asyncio
async def test_update_task_completion_status():
    mock_session = AsyncMock(spec=AsyncSession)
    mock_result = MagicMock()
    mock_task = Task(id="1", title="To Complete", user_id="user123", status=TaskStatus.pending, priority="medium")
    mock_result.scalar_one_or_none.return_value = mock_task
    mock_session.execute = AsyncMock(return_value=mock_result)
    mock_session.commit = AsyncMock()
    mock_session.refresh = AsyncMock()
    
    completion_data = TaskComplete(complete=True)
    
    with pytest.MonkeyPatch().context() as mp:
        mp.setattr("src.services.task_service.Session", lambda x: mock_session)
        updated_task = await update_task_completion_status("1", "user123", completion_data)
        
        assert updated_task is not None
        assert updated_task.status == TaskStatus.completed
        mock_session.commit.assert_called_once()