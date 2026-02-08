# Feature Specification: Phase II Todo Backend

**Feature Branch**: `002-backend-todo-api`  
**Created**: 2026-02-05  
**Status**: Draft  
**Input**: User description: "Backend for Phase II Todo app using FastAPI, SQLModel, Neon Serverless PostgreSQL, Better Auth JWT verification, strict user isolation. Focus: Build a secure, efficient backend that integrates with the frontend – verifies JWT token, enforces user isolation, stores tasks in Neon DB, serves API endpoints correctly."

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Secure Task Management (Priority: P1)

As a registered user, I want to securely manage my tasks through the backend API so that I can add, view, update, delete, and mark tasks as complete while ensuring that I can only access my own tasks.

**Why this priority**: This is the core functionality of the todo application and forms the foundation for all other features.

**Independent Test**: Can be fully tested by authenticating with a JWT token, performing CRUD operations on tasks, and verifying that only the authenticated user's tasks are accessible.

**Acceptance Scenarios**:

1. **Given** user is authenticated with valid JWT token, **When** user requests their tasks, **Then** only tasks belonging to that user are returned
2. **Given** user is authenticated with valid JWT token, **When** user creates a new task, **Then** task is saved with the user's ID and becomes accessible only to that user
3. **Given** user is authenticated with valid JWT token, **When** user attempts to access another user's task, **Then** access is denied with 403 Forbidden error

---

### User Story 2 - JWT Token Verification (Priority: P1)

As a security-conscious user, I want the backend to verify my JWT token from Better Auth so that unauthorized access is prevented and only valid users can interact with the system.

**Why this priority**: Security is paramount to protect user data and prevent unauthorized access to tasks.

**Independent Test**: Can be fully tested by sending requests with valid and invalid JWT tokens and verifying that only valid tokens grant access.

**Acceptance Scenarios**:

1. **Given** user has valid JWT token, **When** user makes API request, **Then** request is processed successfully
2. **Given** user has invalid/expired JWT token, **When** user makes API request, **Then** 401 Unauthorized error is returned
3. **Given** user has no JWT token, **When** user makes API request, **Then** 401 Unauthorized error is returned

---

### User Story 3 - Task Operations with User Isolation (Priority: P2)

As a user, I want to perform all basic CRUD operations on my tasks (create, read, update, delete, mark complete) while being assured that I cannot accidentally access or modify other users' tasks.

**Why this priority**: Ensures data integrity and privacy by maintaining strict user isolation.

**Independent Test**: Can be tested by having multiple users with overlapping task IDs and verifying that each user can only access their own tasks.

**Acceptance Scenarios**:

1. **Given** user has valid JWT token, **When** user updates their task, **Then** only their task is updated and others remain unchanged
2. **Given** user has valid JWT token, **When** user deletes their task, **Then** only their task is deleted and others remain unchanged
3. **Given** user has valid JWT token, **When** user marks their task as complete, **Then** only their task status is changed

---

### Edge Cases

- What happens when a user tries to access a task ID that doesn't belong to them?
- How does the system handle malformed JWT tokens?
- What happens when the database connection fails during an operation?
- How does the system handle concurrent requests from the same user?
- What happens when a user tries to access a non-existent task?

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: System MUST verify JWT tokens using the shared 
- **FR-002**: System MUST extract user_id from the JWT token and validate it against the user_id in the URL
- **FR-003**: System MUST return 401 Unauthorized for invalid/expired JWT tokens
- **FR-004**: System MUST return 403 Forbidden when user_id from token doesn't match user_id in URL
- **FR-005**: System MUST filter all database queries by authenticated user_id to enforce strict user isolation
- **FR-006**: System MUST provide REST API endpoints at /api/{user_id}/tasks for all task operations
- **FR-007**: Users MUST be able to create new tasks via POST /api/{user_id}/tasks
- **FR-008**: Users MUST be able to retrieve their tasks via GET /api/{user_id}/tasks
- **FR-009**: Users MUST be able to retrieve a specific task via GET /api/{user_id}/tasks/{id}
- **FR-010**: Users MUST be able to update a task via PUT /api/{user_id}/tasks/{id}
- **FR-011**: Users MUST be able to delete a task via DELETE /api/{user_id}/tasks/{id}
- **FR-012**: Users MUST be able to mark a task as complete via PATCH /api/{user_id}/tasks/{id}/complete
- **FR-013**: System MUST store tasks in Neon Serverless PostgreSQL database
- **FR-014**: System MUST associate each task with the user who created it via user_id foreign key
- **FR-015**: System MUST accept Bearer token from frontend in Authorization header
- **FR-016**: System MUST return only authenticated user's data based on JWT token verification

### Key Entities *(include if feature involves data)*

- **User**: Represents a registered user with unique identifier (user_id) and email address
- **Task**: Represents a task entity with attributes (id, title, description, status, priority) linked to a User via user_id foreign key

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: All 5 basic CRUD operations work with user isolation: Add/Delete/Update/View tasks, Mark Complete
- **SC-002**: JWT verification using shared BETTER_AUTH_SECRET extracts user_id from token with 100% accuracy
- **SC-003**: All database queries are filtered by authenticated user_id with zero data leakage between users
- **SC-004**: Frontend API calls succeed with Bearer token authentication (95% success rate under normal load)
- **SC-005**: System responds to API requests within 500ms under normal load conditions
- **SC-006**: 100% of unauthorized access attempts are properly blocked with appropriate error codes