# Quickstart Guide: Phase II Todo Backend

## Prerequisites
- Python 3.11+
- pip package manager
- Access to Neon Serverless PostgreSQL database
- BETTER_AUTH_SECRET: jCFvRhqz7MEOLoNE53UWVUIadbgv5lQH

## Setup Instructions

### 1. Clone the Repository
```bash
git clone <repository-url>
cd <repository-directory>
```

### 2. Create Virtual Environment
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Dependencies
```bash
cd backend
pip install fastapi sqlmodel python-jose uvicorn python-multipart python-dotenv
```

### 4. Environment Variables
Create a `.env` file in the backend root:
```env

```

### 5. Initialize the Database
```bash
cd backend
python -c "
from sqlmodel import SQLModel
from src.database.session import engine
from src.models.user import User
from src.models.task import Task

# Import models to register them with SQLModel
from src.database.init_db import create_tables
import asyncio

asyncio.run(create_tables())
"
```

## Running the Application

### Development Mode
```bash
cd backend
uvicorn src.main:app --reload --host 0.0.0.0 --port 8000
```

### Production Mode
```bash
cd backend
uvicorn src.main:app --host 0.0.0.0 --port 8000
```

## Testing the API

### 1. Start the server
```bash
uvicorn src.main:app --reload
```

### 2. Test with curl (replace JWT_TOKEN with a valid token)
```bash
# Get user's tasks
curl -H "Authorization: Bearer JWT_TOKEN" \
     http://localhost:8000/api/user123/tasks

# Create a new task
curl -X POST \
     -H "Authorization: Bearer JWT_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"title":"Test task","description":"Test description","priority":"medium"}' \
     http://localhost:8000/api/user123/tasks
```

## Available Endpoints
- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Mark task as complete/incomplete

## Running Tests
```bash
cd backend
pytest tests/
```