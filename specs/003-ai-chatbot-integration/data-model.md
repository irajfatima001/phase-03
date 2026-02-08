# Data Model: AI-Powered Todo Chatbot Integration

## Overview
This document defines the data models required for the AI-powered todo chatbot integration, extending the existing Phase II models.

## Extended Models

### Conversation Model
Represents a single conversation session between user and AI, containing metadata like user_id, creation time, and update time.

**Fields**:
- id: UUID (primary key)
- user_id: UUID (foreign key to user table, required)
- title: String (optional, auto-generated from first message)
- created_at: DateTime (timestamp, required, default: now)
- updated_at: DateTime (timestamp, required, default: now, auto-update)

**Validation**:
- user_id must reference an existing user
- created_at and updated_at must be valid timestamps

**Relationships**:
- One-to-many with Message model (one conversation has many messages)

### Message Model
Represents an individual message within a conversation, including sender (user/AI), content, and timestamp.

**Fields**:
- id: UUID (primary key)
- conversation_id: UUID (foreign key to conversation table, required)
- user_id: UUID (foreign key to user table, required)
- role: String (required, values: "user", "assistant")
- content: Text (required, message content)
- created_at: DateTime (timestamp, required, default: now)

**Validation**:
- conversation_id must reference an existing conversation
- user_id must reference an existing user
- role must be either "user" or "assistant"
- content must not be empty

**Relationships**:
- Many-to-one with Conversation model (many messages belong to one conversation)
- Many-to-one with User model (many messages associated with one user)

### Extended Task Model (Existing)
The existing Task model from Phase II remains unchanged but will be accessed through the new MCP tools.

**Fields** (existing):
- id: UUID (primary key)
- user_id: UUID (foreign key to user table, required)
- title: String (required)
- description: Text (optional)
- completed: Boolean (required, default: false)
- due_date: Date (optional)
- created_at: DateTime (required, default: now)
- updated_at: DateTime (required, default: now, auto-update)

## State Transitions

### Conversation State
- Created when user initiates first chat
- Updated when new messages are added
- Remains active until user ends session or system cleanup

### Message State
- Created when user sends message or AI responds
- Immutable after creation (no updates allowed)

### Task State (via existing model)
- Created via add_task MCP tool
- Updated via update_task or complete_task MCP tools
- Deleted via delete_task MCP tool
- Always scoped to user_id from JWT token

## Indexes

### Conversation Model
- Index on user_id for efficient user-specific queries
- Index on created_at for chronological ordering

### Message Model
- Index on conversation_id for efficient conversation retrieval
- Index on user_id for user-specific queries
- Composite index on (conversation_id, created_at) for ordered message retrieval

## Constraints

### User Isolation
- All queries must filter by user_id from authenticated JWT token
- Foreign key constraints ensure referential integrity
- Row-level security ensures users can only access their own data

### Data Integrity
- All required fields must be present
- Timestamps automatically managed by database
- UUIDs ensure globally unique identifiers