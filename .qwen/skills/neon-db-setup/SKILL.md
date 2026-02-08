# Skill: neon-db-setup

**Name**: neon-db-setup  
**Description**: Sets up SQLModel async engine, session, and connection for Neon Serverless PostgreSQL using DATABASE_URL from env

## Purpose
This skill sets up the database connection layer for a FastAPI application using SQLModel with Neon Serverless PostgreSQL. It creates an async engine, session factory, and provides utilities for managing database sessions with proper lifecycle management.

## Allowed Tools
- code_write

## Implementation Instructions

### 1. Database Session Setup
```python
# src/database/session.py
from sqlmodel.ext.asyncio.session import AsyncSession, async_sessionmaker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine
from contextlib import asynccontextmanager
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

# Get database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL")

# Handle Neon-specific connection parameters
if DATABASE_URL and "postgresql" in DATABASE_URL:
    # Replace postgresql:// with postgresql+asyncpg:// for async operations
    ASYNC_DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    
    # Handle Neon-specific connection parameters that need adjustment
    # Remove channel_binding parameter which asyncpg doesn't support
    ASYNC_DATABASE_URL = ASYNC_DATABASE_URL.replace("&channel_binding=require", "")
else:
    ASYNC_DATABASE_URL = DATABASE_URL

# Create async engine
engine: AsyncEngine = create_async_engine(ASYNC_DATABASE_URL)

# Create async session maker
AsyncSessionLocal = async_sessionmaker(bind=engine, class_=AsyncSession)
```

### 2. Database Session Context Manager
```python
# src/database/session.py (continued)
from typing import AsyncGenerator

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Async generator to provide database sessions
    """
    async with AsyncSessionLocal() as session:
        yield session
```

### 3. Lifespan Event Handler (Optional)
```python
# src/main.py or wherever your FastAPI app is defined
from contextlib import asynccontextmanager
from fastapi import FastAPI
from sqlmodel import SQLModel
from src.database.session import engine

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize database tables on startup
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)
    yield
    # Cleanup on shutdown
    await engine.dispose()
```

### 4. Example Usage in Dependencies
```python
# src/api/deps.py
from fastapi import Depends
from src.database.session import get_db_session
from sqlmodel.ext.asyncio.session import AsyncSession

async def get_db_session_dep() -> AsyncSession:
    async for session in get_db_session():
        yield session
```

### 5. Example Usage in Services
```python
# src/services/user_service.py
from sqlmodel.ext.asyncio.session import AsyncSession
from src.models.user import User
from sqlmodel import select

async def get_user_by_id(session: AsyncSession, user_id: str) -> User:
    statement = select(User).where(User.id == user_id)
    result = await session.execute(statement)
    return result.scalar_one_or_none()

async def create_user(session: AsyncSession, user: User) -> User:
    session.add(user)
    await session.commit()
    await session.refresh(user)
    return user
```

### 6. Environment Variable Setup
```env
# .env
DATABASE_URL=postgresql://username:password@ep-name.region.aws.neon.tech/dbname?sslmode=require
```

### 7. Requirements
```txt
# requirements.txt
sqlmodel==0.0.16
asyncpg==0.29.0
SQLAlchemy==2.0.46
psycopg2-binary==2.9.9
python-dotenv==1.0.0
```

## Key Features
- Creates an async SQLAlchemy engine using create_async_engine
- Uses async_sessionmaker to create session factories
- Handles Neon-specific connection string adjustments
- Provides async context manager for proper session management
- Includes lifespan event handler for table initialization
- Uses environment variables for database configuration
- Supports SSL connections with sslmode=require
- Compatible with SQLModel and FastAPI

## Security Considerations
- Never hardcode database credentials in the source code
- Always use environment variables for DATABASE_URL
- Ensure the connection uses SSL (sslmode=require)
- Properly dispose of the engine on application shutdown
- Use parameterized queries to prevent SQL injection

## Performance Tips
- Use connection pooling for production applications
- Implement proper indexing strategies for your Neon database
- Monitor slow queries and optimize as needed
- Consider using Neon's branching feature for development environments
- Use async operations throughout to maximize performance benefits