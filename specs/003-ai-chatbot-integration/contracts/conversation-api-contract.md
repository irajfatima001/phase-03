# API Contract: Conversation Endpoints

## Overview
This document defines the API contracts for conversation-related endpoints that will be added to support the AI chatbot functionality.

## Base URL
```
https://api.example.com/api/v1
```

## Authentication
All endpoints require a valid JWT token in the Authorization header:
```
Authorization: Bearer {jwt_token}
```

## Endpoints

### GET /conversations
Retrieve all conversations for the authenticated user.

#### Request
```
GET /conversations
Headers:
  Authorization: Bearer {jwt_token}
```

#### Response
**Success (200 OK)**
```json
{
  "conversations": [
    {
      "id": "uuid-string",
      "title": "Optional title",
      "created_at": "2023-10-01T12:00:00Z",
      "updated_at": "2023-10-01T12:30:00Z"
    }
  ]
}
```

**Unauthorized (401)**
```json
{
  "detail": "Authentication required"
}
```

### GET /conversations/{conversation_id}
Retrieve a specific conversation and its messages.

#### Request
```
GET /conversations/{conversation_id}
Headers:
  Authorization: Bearer {jwt_token}
```

#### Response
**Success (200 OK)**
```json
{
  "id": "uuid-string",
  "title": "Optional title",
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:30:00Z",
  "messages": [
    {
      "id": "uuid-string",
      "role": "user",
      "content": "Add task: Buy groceries",
      "created_at": "2023-10-01T12:15:00Z"
    },
    {
      "id": "uuid-string",
      "role": "assistant",
      "content": "I've added 'Buy groceries' to your tasks.",
      "created_at": "2023-10-01T12:15:05Z"
    }
  ]
}
```

**Unauthorized (401)**
```json
{
  "detail": "Authentication required"
}
```

**Forbidden (403)**
```json
{
  "detail": "Access denied"
}
```

### POST /conversations
Create a new conversation.

#### Request
```
POST /conversations
Headers:
  Authorization: Bearer {jwt_token}
Content-Type: application/json
Body:
{
  "title": "Optional title"
}
```

#### Response
**Success (201 Created)**
```json
{
  "id": "uuid-string",
  "title": "Optional title",
  "created_at": "2023-10-01T12:00:00Z",
  "updated_at": "2023-10-01T12:00:00Z"
}
```

**Unauthorized (401)**
```json
{
  "detail": "Authentication required"
}
```

### POST /conversations/{conversation_id}/messages
Add a message to a conversation and get AI response.

#### Request
```
POST /conversations/{conversation_id}/messages
Headers:
  Authorization: Bearer {jwt_token}
Content-Type: application/json
Body:
{
  "content": "Natural language command for the AI"
}
```

#### Response
**Success (201 Created)**
```json
{
  "user_message": {
    "id": "uuid-string",
    "role": "user",
    "content": "Natural language command for the AI",
    "created_at": "2023-10-01T12:15:00Z"
  },
  "ai_response": {
    "id": "uuid-string",
    "role": "assistant",
    "content": "AI's response to the command",
    "created_at": "2023-10-01T12:15:05Z"
  }
}
```

**Unauthorized (401)**
```json
{
  "detail": "Authentication required"
}
```

**Forbidden (403)**
```json
{
  "detail": "Access denied"
}
```

### POST /conversations/initiate
Initiate a new conversation with a message.

#### Request
```
POST /conversations/initiate
Headers:
  Authorization: Bearer {jwt_token}
Content-Type: application/json
Body:
{
  "message": "Natural language command for the AI"
}
```

#### Response
**Success (201 Created)**
```json
{
  "conversation_id": "uuid-string",
  "user_message": {
    "id": "uuid-string",
    "role": "user",
    "content": "Natural language command for the AI",
    "created_at": "2023-10-01T12:15:00Z"
  },
  "ai_response": {
    "id": "uuid-string",
    "role": "assistant",
    "content": "AI's response to the command",
    "created_at": "2023-10-01T12:15:05Z"
  }
}
```

**Unauthorized (401)**
```json
{
  "detail": "Authentication required"
}
```

## Error Handling
All endpoints follow standard HTTP status codes:
- 200: Success
- 201: Created
- 400: Bad Request (invalid input)
- 401: Unauthorized (missing or invalid JWT)
- 403: Forbidden (user doesn't have access to resource)
- 404: Not Found (resource doesn't exist)
- 500: Internal Server Error

## Validation Rules
- All requests must include a valid JWT token
- User can only access their own conversations and messages
- Message content must not be empty
- Conversation titles are optional but if provided must be under 100 characters