# Tasks: Phase II Todo Backend

## Feature Overview
Build a secure, efficient backend for the Phase II Todo app using FastAPI, SQLModel, and Neon Serverless PostgreSQL. The backend will verify JWT tokens from Better Auth, enforce strict user isolation (each user only sees/modifies own tasks), and serve REST API endpoints correctly.

## Phase 1: Setup
Initialize project structure and dependencies

### Goal
Create the foundational project structure and install required dependencies

### Independent Test Criteria
- Project directory structure matches planned architecture
- All dependencies are properly installed and accessible
- Basic project can be run without errors

### Implementation Tasks

- [ ] T001 Create backend directory structure: models, services, api, database, utils, tests
- [ ] T002 [P] Create requirements.txt with FastAPI, SQLModel, python-jose, pydantic, psycopg2-binary
- [ ] T003 [P] Create main.py file in backend root directory
- [ ] T004 [P] Create .env file with DATABASE_URL and BETTER_AUTH_SECRET variables
- [ ] T005 Install dependencies using pip install -r requirements.txt

## Phase 2: Foundational Components
Create foundational components that all user stories depend on

### Goal
Implement core components that are prerequisites for all user stories

### Independent Test Criteria
- Database connection can be established
- JWT utilities can encode/decode tokens
- Authentication dependency works correctly
- User and Task models are properly defined

### Implementation Tasks

- [ ] T006 Create database/session.py with async SQLModel engine configuration
- [ ] T007 [P] Create models/user.py with User model definition per data model
- [ ] T008 [P] Create models/task.py with Task model definition per data model
- [ ] T009 Create utils/jwt_utils.py with JWT verification functions using BETTER_AUTH_SECRET
- [ ] T010 Create api/deps.py with JWT authentication dependency
- [ ] T011 Create database initialization script to create tables

## Phase 3: User Story 1 - Secure Task Management (Priority: P1)

### Goal
Enable registered users to securely manage their tasks through the backend API, allowing them to add, view, update, delete, and mark tasks as complete while ensuring they can only access their own tasks.

### Independent Test Criteria
- User can authenticate with JWT token and perform CRUD operations on tasks
- Only authenticated user's tasks are returned when requesting tasks
- New tasks are saved with user's ID and are accessible only to that user
- User cannot access another user's tasks (access denied with 403 Forbidden error)

### Acceptance Scenarios
1. Given user is authenticated with valid JWT token, When user requests their tasks, Then only tasks belonging to that user are returned
2. Given user is authenticated with valid JWT token, When user creates a new task, Then task is saved with the user's ID and becomes accessible only to that user
3. Given user is authenticated with valid JWT token, When user attempts to access another user's task, Then access is denied with 403 Forbidden error

### Implementation Tasks

- [ ] T012 [P] [US1] Create service layer in services/task_service.py with CRUD operations
- [ ] T013 [P] [US1] Create API routes in api/tasks.py for GET /api/{user_id}/tasks
- [ ] T014 [P] [US1] Implement POST /api/{user_id}/tasks endpoint in api/tasks.py
- [ ] T015 [US1] Implement GET /api/{user_id}/tasks/{id} endpoint in api/tasks.py
- [ ] T016 [US1] Implement PUT /api/{user_id}/tasks/{id} endpoint in api/tasks.py
- [ ] T017 [US1] Implement DELETE /api/{user_id}/tasks/{id} endpoint in api/tasks.py
- [ ] T018 [US1] Implement PATCH /api/{user_id}/tasks/{id}/complete endpoint in api/tasks.py

## Phase 4: User Story 2 - JWT Token Verification (Priority: P1)

### Goal
Verify JWT tokens from Better Auth to prevent unauthorized access and ensure only valid users can interact with the system.

### Independent Test Criteria
- Requests with valid JWT tokens are processed successfully
- Requests with invalid/expired JWT tokens return 401 Unauthorized error
- Requests with no JWT token return 401 Unauthorized error
- User_id is correctly extracted from JWT token

### Acceptance Scenarios
1. Given user has valid JWT token, When user makes API request, Then request is processed successfully
2. Given user has invalid/expired JWT token, When user makes API request, Then 401 Unauthorized error is returned
3. Given user has no JWT token, When user makes API request, Then 401 Unauthorized error is returned

### Implementation Tasks

- [ ] T019 [P] [US2] Enhance JWT utilities to properly validate tokens using BETTER_AUTH_SECRET
- [ ] T020 [US2] Update authentication dependency to extract user_id from JWT token
- [ ] T021 [US2] Implement token validation in all API endpoints
- [ ] T022 [US2] Add proper 401 error handling for invalid/missing tokens

## Phase 5: User Story 3 - Task Operations with User Isolation (Priority: P2)

### Goal
Allow users to perform all basic CRUD operations on their tasks while ensuring they cannot accidentally access or modify other users' tasks.

### Independent Test Criteria
- When user updates their task, only their task is updated and others remain unchanged
- When user deletes their task, only their task is deleted and others remain unchanged
- When user marks their task as complete, only their task status is changed
- All database queries are filtered by authenticated user_id with zero data leakage between users

### Acceptance Scenarios
1. Given user has valid JWT token, When user updates their task, Then only their task is updated and others remain unchanged
2. Given user has valid JWT token, When user deletes their task, Then only their task is deleted and others remain unchanged
3. Given user has valid JWT token, When user marks their task as complete, Then only their task status is changed

### Implementation Tasks

- [ ] T023 [P] [US3] Update task service to filter all queries by authenticated user_id
- [ ] T024 [US3] Add user_id validation to ensure token user_id matches URL user_id
- [ ] T025 [US3] Implement 403 Forbidden error when user_id from token doesn't match URL
- [ ] T026 [US3] Add comprehensive user isolation checks in all task operations

## Phase 6: Error Handling and Validation
Implement proper error handling and validation across all components

### Goal
Ensure all endpoints implement proper error handling with appropriate HTTP status codes

### Independent Test Criteria
- Appropriate 401/403/404/500 responses for different error conditions
- Validation errors are properly handled and returned to clients
- Error responses follow the defined API contract format

### Implementation Tasks

- [ ] T027 Implement global exception handlers for common errors
- [ ] T028 [P] Add input validation to all API endpoints using Pydantic models
- [ ] T029 Standardize error response format per API contract
- [ ] T030 Add comprehensive logging for debugging purposes

## Phase 7: Testing and Documentation
Create tests and enable API documentation

### Goal
Ensure all functionality is properly tested and documented

### Independent Test Criteria
- All endpoints tested with valid and invalid inputs
- End-to-end workflows function correctly with proper authentication
- Interactive API documentation is available

### Implementation Tasks

- [ ] T031 Create unit tests for all service functions
- [ ] T032 [P] Create integration tests for all API endpoints
- [ ] T033 [P] Create conftest.py with test fixtures for database and authentication
- [ ] T034 Enable FastAPI's automatic documentation
- [ ] T035 Run all tests to ensure functionality works as expected

## Phase 8: Polish & Cross-Cutting Concerns
Final touches and integration validation

### Goal
Complete integration testing and ensure all requirements are met

### Independent Test Criteria
- Frontend successfully calls backend API with JWT authentication
- API responds within 500ms under normal load conditions
- All security requirements met per specification
- 100% of unauthorized access attempts are properly blocked with appropriate error codes

### Implementation Tasks

- [ ] T036 Perform security validation to ensure all measures are in place
- [ ] T037 [P] Test complete workflows with JWT tokens and database operations
- [ ] T038 [P] Verify response times under normal load conditions
- [ ] T039 Test API endpoints from frontend with Bearer tokens
- [ ] T040 Final validation of all functional requirements

## Dependencies

### User Story Completion Order
1. User Story 1 (Secure Task Management) - Foundation for all task operations
2. User Story 2 (JWT Token Verification) - Security layer for authentication
3. User Story 3 (Task Operations with User Isolation) - Advanced security for data isolation

### Critical Path
T001 → T002 → T003 → T004 → T005 → T006 → T007 → T008 → T009 → T010 → T011 → T012 → T013 → T014 → T015 → T016 → T017 → T018

## Parallel Execution Examples

### Per User Story
- **User Story 1**: Tasks T012-T018 can be developed in parallel by different developers
- **Foundational Phase**: Tasks T006-T011 can be developed in parallel after T001-T005 are complete

## Implementation Strategy

### MVP First Approach
1. Start with User Story 1 (Secure Task Management) as the core functionality
2. Implement basic CRUD operations for tasks with user authentication
3. Add security features (User Stories 2 and 3) in subsequent iterations
4. Complete with testing, documentation, and polish

### Incremental Delivery
- **Iteration 1**: Basic project setup and foundational components (Phases 1-2)
- **Iteration 2**: Core task management functionality (User Story 1)
- **Iteration 3**: Authentication and security (User Story 2)
- **Iteration 4**: User isolation and advanced security (User Story 3)
- **Iteration 5**: Testing, documentation, and final validation (Phases 6-8)