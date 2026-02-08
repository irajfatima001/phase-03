import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.session import engine
from src.models.user import User
from src.models.task import Task, TaskStatus, TaskPriority
from src.utils.jwt_utils import create_access_token
from datetime import timedelta
import os

# Set environment variable for testing
os.environ["BETTER_AUTH_SECRET"] = "test-secret-key-for-testing"


@pytest.fixture
def mock_db_session():
    """Mock database session fixture"""
    session = AsyncMock(spec=AsyncSession)
    session.commit = AsyncMock()
    session.refresh = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def valid_user_id():
    """Valid user ID for testing"""
    return "test_user_123"


@pytest.fixture
def valid_task_data(valid_user_id):
    """Valid task data for testing"""
    return {
        "title": "Test Task",
        "description": "Test Description",
        "status": TaskStatus.pending,
        "priority": TaskPriority.medium,
        "user_id": valid_user_id
    }


@pytest.fixture
def valid_token(valid_user_id):
    """Valid JWT token for testing"""
    data = {"sub": valid_user_id}
    return create_access_token(data, expires_delta=timedelta(minutes=30))


@pytest.fixture
def invalid_token():
    """Invalid JWT token for testing"""
    return "invalid_token_here"