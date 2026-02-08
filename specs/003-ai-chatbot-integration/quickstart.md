# Quickstart Guide: AI-Powered Todo Chatbot Integration

## Overview
This guide provides a quick setup and usage guide for the AI-powered todo chatbot integration.

## Prerequisites
- Node.js 18+ for frontend
- Python 3.11+ for backend
- Neon PostgreSQL database
- Better Auth configured


## Setup Instructions

### 1. Environment Configuration
Set up the following environment variables:

Backend (.env):
```

```

### 2. Backend Setup
1. Install backend dependencies:
```bash
cd backend
pip install -r requirements.txt
```

2. Run database migrations:
```bash
cd backend
alembic upgrade head
```

3. Start the backend server:
```bash
cd backend
uvicorn src.main:app --reload
```

4. In a separate terminal, start the MCP server:
```bash
cd backend
python -m src.api.mcp.server
```

### 3. Frontend Setup
1. Install frontend dependencies:
```bash
cd frontend
npm install
```

2. Start the frontend development server:
```bash
cd frontend
npm run dev
```

## Usage Instructions

### 1. Access the Dashboard
Navigate to `http://localhost:3000` and log in with your credentials.

### 2. Using the Chatbot
1. Navigate to the dashboard where the chatbot component is embedded
2. Type natural language commands such as:
   - "Add task: Buy milk tomorrow"
   - "Show my pending tasks"
   - "Mark gym as complete"
   - "Delete task 3"
   - "Update task 1 to call mom"

### 3. Conversation History
- Previous conversations are stored and accessible
- Context is maintained within the same conversation session
- History persists between sessions

## Verification Steps

### 1. Verify Backend API
- Confirm that the existing `/api/{user_id}/tasks` endpoints are accessible
- Verify that the new MCP server is running and exposing tools

### 2. Verify Database Models
- Confirm that Conversation and Message tables exist in the database
- Verify that new records are created when users interact with the chatbot

### 3. Verify User Isolation
- Log in as different users and confirm they can only see their own tasks and conversations

### 4. Verify Cohere Integration
- Test that natural language commands are properly interpreted
- Confirm that the AI responds appropriately to various task management requests

## Troubleshooting

### Common Issues
1. **Cohere API errors**: Verify that the COHERE_API_KEY is correctly set
2. **Authentication errors**: Ensure JWT tokens are properly passed from frontend to backend
3. **Database connection errors**: Check that DATABASE_URL is correctly configured
4. **MCP tools not available**: Verify that the MCP server is running alongside the main API server

### Testing Commands
Try these commands to verify functionality:
- "Add task: Test the chatbot integration"
- "List my tasks"
- "Mark test task as complete"
- "Delete test task"