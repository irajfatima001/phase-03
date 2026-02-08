import pytest
from httpx import AsyncClient
from main import app
from src.models.task import Task, TaskStatus, TaskPriority
from unittest.mock import patch, AsyncMock


@pytest.mark.asyncio
async def test_get_tasks():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        # Mock the service function
        with patch("src.services.task_service.get_tasks_by_user_id", new_callable=AsyncMock) as mock_service:
            mock_service.return_value = [
                Task(id="1", title="Test Task", user_id="user123", status=TaskStatus.pending, priority=TaskPriority.medium)
            ]
            
            response = await ac.get("/api/user123/tasks", headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 200
            data = response.json()
            assert len(data) == 1
            assert data[0]["title"] == "Test Task"


@pytest.mark.asyncio
async def test_create_task():
    task_data = {
        "title": "New Task",
        "description": "Test description",
        "status": "pending",
        "priority": "medium",
        "user_id": "user123"
    }
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("src.services.task_service.create_task_for_user_id", new_callable=AsyncMock) as mock_service:
            mock_task = Task(**task_data, id="1")
            mock_service.return_value = mock_task
            
            response = await ac.post("/api/user123/tasks", json=task_data, headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 201
            data = response.json()
            assert data["title"] == "New Task"


@pytest.mark.asyncio
async def test_get_specific_task():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("src.services.task_service.get_task_by_id_and_user_id", new_callable=AsyncMock) as mock_service:
            task = Task(id="1", title="Specific Task", user_id="user123", status=TaskStatus.pending, priority=TaskPriority.medium)
            mock_service.return_value = task
            
            response = await ac.get("/api/user123/tasks/1", headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Specific Task"


@pytest.mark.asyncio
async def test_update_task():
    update_data = {"title": "Updated Task"}
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("src.services.task_service.update_task_by_id_and_user_id", new_callable=AsyncMock) as mock_service:
            updated_task = Task(id="1", title="Updated Task", user_id="user123", status=TaskStatus.pending, priority=TaskPriority.medium)
            mock_service.return_value = updated_task
            
            response = await ac.put("/api/user123/tasks/1", json=update_data, headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["title"] == "Updated Task"


@pytest.mark.asyncio
async def test_delete_task():
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("src.services.task_service.delete_task_by_id_and_user_id", new_callable=AsyncMock) as mock_service:
            mock_service.return_value = True  # Simulate successful deletion
            
            response = await ac.delete("/api/user123/tasks/1", headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 204


@pytest.mark.asyncio
async def test_update_task_completion():
    completion_data = {"complete": True}
    
    async with AsyncClient(app=app, base_url="http://testserver") as ac:
        with patch("src.services.task_service.update_task_completion_status", new_callable=AsyncMock) as mock_service:
            completed_task = Task(id="1", title="Completed Task", user_id="user123", status=TaskStatus.completed, priority=TaskPriority.medium)
            mock_service.return_value = completed_task
            
            response = await ac.patch("/api/user123/tasks/1/complete", json=completion_data, headers={"Authorization": "Bearer fake_token"})
            
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "completed"