# MCP Contract: Task Operation Tools

## Overview
This document defines the MCP (Model Context Protocol) tools that will be exposed for the AI agent to perform task operations.

## Tools

### add_task
Add a new task to the user's task list.

#### Parameters
```json
{
  "title": {
    "type": "string",
    "description": "The title of the task to add",
    "required": true
  },
  "description": {
    "type": "string",
    "description": "Optional description of the task",
    "required": false
  },
  "due_date": {
    "type": "string",
    "format": "date",
    "description": "Optional due date in YYYY-MM-DD format",
    "required": false
  }
}
```

#### Response
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "task_id": {
    "type": "string",
    "description": "The ID of the newly created task"
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the result"
  }
}
```

#### Example
```json
{
  "title": "Buy groceries",
  "description": "Milk, bread, eggs",
  "due_date": "2023-10-15"
}
```

### list_tasks
Retrieve the user's tasks with optional filtering.

#### Parameters
```json
{
  "status": {
    "type": "string",
    "enum": ["all", "pending", "completed"],
    "description": "Filter tasks by status",
    "required": false,
    "default": "all"
  }
}
```

#### Response
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "tasks": {
    "type": "array",
    "items": {
      "type": "object",
      "properties": {
        "id": {"type": "string"},
        "title": {"type": "string"},
        "description": {"type": "string"},
        "completed": {"type": "boolean"},
        "due_date": {"type": "string", "format": "date"},
        "created_at": {"type": "string", "format": "date-time"},
        "updated_at": {"type": "string", "format": "date-time"}
      }
    }
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the result"
  }
}
```

#### Example
```json
{
  "status": "pending"
}
```

### complete_task
Mark a task as completed.

#### Parameters
```json
{
  "task_id": {
    "type": "string",
    "description": "The ID of the task to mark as complete",
    "required": true
  }
}
```

#### Response
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the result"
  }
}
```

#### Example
```json
{
  "task_id": "task-uuid-string"
}
```

### delete_task
Delete a task from the user's task list.

#### Parameters
```json
{
  "task_id": {
    "type": "string",
    "description": "The ID of the task to delete",
    "required": true
  }
}
```

#### Response
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the result"
  }
}
```

#### Example
```json
{
  "task_id": "task-uuid-string"
}
```

### update_task
Update an existing task's properties.

#### Parameters
```json
{
  "task_id": {
    "type": "string",
    "description": "The ID of the task to update",
    "required": true
  },
  "title": {
    "type": "string",
    "description": "New title for the task (optional)",
    "required": false
  },
  "description": {
    "type": "string",
    "description": "New description for the task (optional)",
    "required": false
  },
  "due_date": {
    "type": "string",
    "format": "date",
    "description": "New due date for the task in YYYY-MM-DD format (optional)",
    "required": false
  },
  "completed": {
    "type": "boolean",
    "description": "Whether the task is completed (optional)",
    "required": false
  }
}
```

#### Response
```json
{
  "success": {
    "type": "boolean",
    "description": "Whether the operation was successful"
  },
  "message": {
    "type": "string",
    "description": "Human-readable message about the result"
  }
}
```

#### Example
```json
{
  "task_id": "task-uuid-string",
  "title": "Updated task title",
  "completed": true
}
```

## Authentication
All tools automatically receive the user's authentication context from the MCP server, ensuring that all operations are scoped to the authenticated user only.

## Error Handling
All tools follow a consistent error response format:
```json
{
  "success": false,
  "message": "Descriptive error message",
  "error_code": "human_readable_error_code"
}
```

## Validation
- All required parameters must be provided
- Task IDs must exist and belong to the authenticated user
- Dates must be in valid YYYY-MM-DD format
- User isolation is enforced at the server level