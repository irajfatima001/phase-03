# AI-Powered Todo Chatbot Integration

This project integrates an AI chatbot into the existing Todo application, allowing users to manage their tasks using natural language commands.

## Features

- Natural language task management (add, delete, update, mark complete, list tasks)
- Conversation history with context preservation
- User isolation - each user can only access their own tasks and conversations
- Cohere AI integration for natural language processing
- MCP tools for AI to interact with task operations

## Tech Stack

- Backend: FastAPI, SQLModel, PostgreSQL, Cohere API, MCP
- Frontend: Next.js 14+, React, TypeScript
- Authentication: Better Auth with JWT
- Database: PostgreSQL (Neon)

## Prerequisites

- Python 3.11+
- Node.js 18+
- PostgreSQL database
- Cohere API key

## Setup Instructions

### Backend Setup

1. Navigate to the backend directory:
```bash
cd /mnt/d/phase 3/backend
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
# Edit .env with your configuration
```

5. Run the backend:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. Navigate to the frontend directory:
```bash
cd /mnt/d/phase 3/frontend
```

2. Install dependencies:
```bash
npm install
```

3. Run the development server:
```bash
npm run dev
```

## Environment Variables

### Backend (.env)
- `DATABASE_URL`: PostgreSQL database connection string
- `BETTER_AUTH_SECRET`: Secret key for JWT authentication
- `COHERE_API_KEY`: Cohere API key for AI operations

### Frontend (.env.local)
- `NEXT_PUBLIC_API_URL`: Backend API URL (default: http://localhost:8000)

## API Endpoints

- `GET /api/v1/conversations` - Get all conversations for the user
- `GET /api/v1/conversations/{id}` - Get a specific conversation with messages
- `POST /api/v1/conversations` - Create a new conversation
- `POST /api/v1/conversations/initiate` - Initiate a conversation with a message
- `POST /api/v1/conversations/{id}/messages` - Add a message to a conversation

## Architecture

- Backend: FastAPI with SQLModel and PostgreSQL
- Frontend: Next.js 14+ with App Router
- Authentication: Better Auth with JWT
- AI Integration: Cohere API with MCP tools
- Database: PostgreSQL with Conversation and Message models

## Running the Application

1. Start the backend server (port 8000)
2. Start the frontend server (port 3000)
3. Access the application at http://localhost:3000

The AI chatbot is integrated into the dashboard and can be used to manage tasks using natural language commands.