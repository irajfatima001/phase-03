# Phase II Todo App Backend

This is the backend service for the Phase II Todo app, built with FastAPI, SQLModel, and Neon Serverless PostgreSQL.

## Features

- JWT token authentication using Better Auth
- User isolation - each user only sees their own tasks
- Full CRUD operations for tasks
- Task completion marking
- Async database operations with Neon PostgreSQL

## Tech Stack

- Python 3.11
- FastAPI
- SQLModel
- python-jose (for JWT handling)
- Neon Serverless PostgreSQL
- Pydantic for validation

## Setup

1. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

2. Set up environment variables in `.env`:
   ```
   DATABASE_URL=postgresql://neondb_owner:npg_CQUc0p5yLlde@ep-holy-rice-a7hoz5fi-pooler.ap-southeast-2.aws.neon.tech/neondb?sslmode=require&channel_binding=require
   BETTER_AUTH_SECRET=jCFvRhqz7MEOLoNE53UWVUIadbgv5lQH
   ```

3. Run the application:
   ```bash
   uvicorn main:app --reload
   ```

## API Endpoints

All endpoints require a valid JWT token in the Authorization header: `Authorization: Bearer <token>`

- `GET /api/{user_id}/tasks` - Get all tasks for a user
- `POST /api/{user_id}/tasks` - Create a new task for a user
- `GET /api/{user_id}/tasks/{id}` - Get a specific task
- `PUT /api/{user_id}/tasks/{id}` - Update a specific task
- `DELETE /api/{user_id}/tasks/{id}` - Delete a specific task
- `PATCH /api/{user_id}/tasks/{id}/complete` - Mark task as complete/incomplete

## Security

- JWT tokens are verified using the shared BETTER_AUTH_SECRET
- All endpoints enforce user isolation by checking that the user_id in the token matches the user_id in the URL
- 401 Unauthorized errors for invalid/missing tokens
- 403 Forbidden errors when user_id from token doesn't match URL parameter

## Testing

Run the tests with:
```bash
pytest tests/
```