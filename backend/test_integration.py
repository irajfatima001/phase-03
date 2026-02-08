import asyncio
import uuid
from sqlmodel import SQLModel, select
from sqlmodel.ext.asyncio.session import AsyncSession
from src.database.session import engine
from src.models.task import Task, TaskCreate, TaskStatus, TaskPriority
from src.models.user import User


async def test_database_connection():
    """Test basic database connection and operations"""
    print("Testing database connection...")
    try:
        async with AsyncSession(engine) as session:
            # Test creating a user
            user_id = str(uuid.uuid4())
            user = User(
                id=user_id,
                email=f"test_{str(uuid.uuid4())[:8]}@example.com"
            )
            
            # Test creating a task
            task_data = TaskCreate(
                title="Test Task",
                description="This is a test task",
                status=TaskStatus.pending,
                priority=TaskPriority.medium,
                user_id=user_id
            )
            
            task = Task(
                id=str(uuid.uuid4()),
                title=task_data.title,
                description=task_data.description,
                status=task_data.status,
                priority=task_data.priority,
                user_id=task_data.user_id
            )
            
            session.add(task)
            await session.commit()
            await session.refresh(task)
            
            print(f"✓ Successfully created task: {task.title}")
            print(f"  Task ID: {task.id}")
            print(f"  User ID: {task.user_id}")
            print(f"  Status: {task.status}")
            print(f"  Priority: {task.priority}")
            
            # Test retrieving tasks for the user
            statement = select(Task).where(Task.user_id == user_id)
            result = await session.execute(statement)
            user_tasks = result.scalars().all()
            
            print(f"✓ Retrieved {len(user_tasks)} tasks for user {user_id}")
            
            # Clean up - delete the test task
            await session.delete(task)
            await session.commit()
            
            print("✓ Database connection test passed!")
            return True
            
    except Exception as e:
        print(f"✗ Database connection test failed: {e}")
        return False


async def main():
    print("Running backend integration tests...\n")
    
    # Test database connection
    db_success = await test_database_connection()
    
    if db_success:
        print("\n✓ All backend integration tests passed!")
    else:
        print("\n✗ Some backend integration tests failed!")
        exit(1)


if __name__ == "__main__":
    asyncio.run(main())