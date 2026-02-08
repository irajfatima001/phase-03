# Data Model: Phase II Todo Backend

## User Entity
- **id**: String (primary key) - Unique identifier for the user
- **email**: String - User's email address for identification
- **createdAt**: DateTime - Timestamp when user account was created
- **updatedAt**: DateTime - Timestamp when user account was last updated

## Task Entity
- **id**: String (primary key) - Unique identifier for the task
- **title**: String (required, max 255 chars) - Brief title of the task
- **description**: Text (optional) - Detailed description of the task
- **status**: Enum (pending, in_progress, completed) - Current status of the task
- **priority**: Enum (low, medium, high) - Priority level of the task
- **userId**: String (foreign key) - Links task to the owning user
- **createdAt**: DateTime - Timestamp when task was created
- **updatedAt**: DateTime - Timestamp when task was last updated
- **completedAt**: DateTime (nullable) - Timestamp when task was marked as completed

## Relationships
- **User to Tasks**: One-to-many relationship (one user can have many tasks)
- **Task to User**: Many-to-one relationship (many tasks belong to one user)

## Validation Rules
- Task title must not be empty
- Task status must be one of the allowed values (pending, in_progress, completed)
- Task priority must be one of the allowed values (low, medium, high)
- Task.userId must reference an existing User.id
- User.email must be a valid email format

## State Transitions
- Task.status can transition from 'pending' to 'in_progress' to 'completed'
- Task.status can transition from 'completed' back to 'pending' (for reopened tasks)
- When status changes to 'completed', completed_at field is set to current timestamp
- When status changes from 'completed' to any other status, completed_at field is cleared