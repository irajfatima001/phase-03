# Implementation Plan: Phase II Todo Backend

**Branch**: `002-backend-todo-api` | **Date**: 2026-02-05 | **Spec**: [link](spec.md)
**Input**: Feature specification from `specs/002-backend-todo-api/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Build a secure, efficient backend for the Phase II Todo app using FastAPI, SQLModel, and Neon Serverless PostgreSQL. The backend will verify JWT tokens from Better Auth, enforce strict user isolation (each user only sees/modifies own tasks), and serve REST API endpoints correctly. The implementation will follow clean architecture principles with proper separation of concerns, async patterns, and Pydantic validation to ensure security and prevent data leakage between users.

## Technical Context

**Language/Version**: Python 3.11
**Primary Dependencies**: FastAPI, SQLModel, python-jose, pydantic, Neon PostgreSQL driver
**Storage**: Neon Serverless PostgreSQL database accessed via async SQLModel engine
**Testing**: pytest for unit/integration tests
**Target Platform**: Linux server (backend API service)
**Project Type**: Web application backend (REST API)
**Performance Goals**: <500ms response time for API endpoints under normal load
**Constraints**: JWT token verification using BETTER_AUTH_SECRET, strict user isolation, async database operations
**Scale/Scope**: Individual user task management with proper authentication and authorization

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**GATE PASS**: This plan complies with all constitution requirements:
- All code will be generated exclusively through Qwen Code CLI using sub-agents (backend-architect, auth-specialist, security-isolator)
- Every database query will filter by user_id to ensure strict user isolation
- JWT tokens issued by Better Auth will be verified using shared BETTER_AUTH_SECRET
- All code will follow clean architecture principles with proper separation of concerns
- Frontend will pass JWT Bearer tokens in API requests to backend endpoints
- Database operations will use SQLModel ORM exclusively with Neon Serverless PostgreSQL
- All endpoints will implement proper error handling with appropriate HTTP status codes

## Project Structure

### Documentation (this feature)

```text
specs/002-backend-todo-api/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

backend/
├── src/
│   ├── models/
│   │   ├── user.py
│   │   └── task.py
│   ├── services/
│   │   ├── auth_service.py
│   │   └── task_service.py
│   ├── api/
│   │   ├── deps.py
│   │   ├── auth.py
│   │   └── tasks.py
│   ├── database/
│   │   └── session.py
│   └── utils/
│       └── jwt_utils.py
└── tests/
    ├── unit/
    ├── integration/
    └── conftest.py

**Structure Decision**: Web application backend structure selected as the feature requires a FastAPI backend service that integrates with the existing frontend. The backend will contain models, services, API routes, database utilities, and JWT utilities.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [e.g., 4th project] | [current need] | [why 3 projects insufficient] |
| [e.g., Repository pattern] | [specific problem] | [why direct DB access insufficient] |

## Backend Development Plan for Phase II Todo Full-Stack Web Application (Hackathon II)

### Overview
Build a secure, efficient backend that fully integrates with the frontend – verifies JWT token from Better Auth, enforces strict user isolation (each user only sees/modifies own tasks), stores tasks in Neon DB, and serves API endpoints correctly.

### Step-by-Step Plan

1. **Setup Project Structure**: Create the backend directory structure with models, services, api, database, and utils folders
   - Use: backend-architect skill
   - Success criteria: Directory structure matches planned architecture

2. **Configure Dependencies**: Install FastAPI, SQLModel, python-jose, pydantic, and other required packages
   - Use: backend-architect skill
   - Success criteria: All dependencies properly installed and accessible

3. **Create Database Models**: Implement User and Task models with proper relationships and validation
   - Use: backend-architect, neon-db-setup skills
   - Success criteria: Models properly define entities with relationships and validation rules

4. **Setup Database Connection**: Configure async SQLModel engine with Neon PostgreSQL connection
   - Use: neon-db-setup skill
   - Success criteria: Successful connection to Neon database with async operations

5. **Implement JWT Utilities**: Create JWT verification functions using python-jose and BETTER_AUTH_SECRET
   - Use: auth-specialist, jwt-middleware skills
   - Success criteria: JWT tokens verified with 100% accuracy, user_id extracted correctly

6. **Create Authentication Dependencies**: Implement FastAPI dependency for JWT verification
   - Use: auth-specialist skill
   - Success criteria: Dependency properly validates tokens and extracts user_id

7. **Design Task Service Layer**: Create service functions for all CRUD operations with user isolation
   - Use: backend-architect, user-isolation-filter skills
   - Success criteria: All database queries filtered by authenticated user_id

8. **Implement Task API Routes**: Create all required endpoints at /api/{user_id}/tasks
   - Use: backend-architect skill
   - Success criteria: All 5 basic CRUD operations work with user isolation

9. **Add User Isolation Logic**: Ensure all endpoints verify user_id from token matches URL parameter
   - Use: security-isolator skill
   - Success criteria: 100% of unauthorized access attempts blocked with 403 errors

10. **Implement Error Handling**: Add proper HTTP status codes and error responses
    - Use: backend-architect skill
    - Success criteria: Appropriate 401/403/404/500 responses for different error conditions

11. **Create API Documentation**: Enable FastAPI's automatic documentation
    - Use: backend-architect skill
    - Success criteria: Interactive API documentation available at /docs

12. **Write Unit Tests**: Create tests for all endpoints and service functions
    - Use: backend-architect skill
    - Success criteria: All endpoints tested with valid and invalid inputs

13. **Integration Testing**: Test complete workflows with JWT tokens and database operations
    - Use: backend-architect, security-isolator skills
    - Success criteria: End-to-end workflows function correctly with proper authentication

14. **Performance Testing**: Verify response times under normal load
    - Use: backend-architect skill
    - Success criteria: API responds within 500ms under normal load conditions

15. **Security Validation**: Verify all security measures are in place
    - Use: security-isolator skill
    - Success criteria: All security requirements met per specification

16. **Frontend Integration**: Test API endpoints from frontend with Bearer tokens
    - Use: backend-architect, auth-specialist skills
    - Success criteria: Frontend successfully calls backend API with JWT authentication

### Integration Checkpoints

- **After Step 8**: Test basic task creation and retrieval with JWT authentication
  - curl command: `curl -H "Authorization: Bearer VALID_JWT_TOKEN" http://localhost:8000/api/user123/tasks`

- **After Step 9**: Test user isolation by attempting to access another user's tasks
  - curl command: `curl -H "Authorization: Bearer_USER1_TOKEN" http://localhost:8000/api/user2/tasks` (should return 403)

- **After Step 12**: Test all CRUD operations with proper authentication
  - Frontend call: `fetch('/api/user123/tasks', { headers: { 'Authorization': 'Bearer TOKEN' }})`

- **After Step 16**: Complete integration test with frontend calling all backend endpoints
  - Frontend workflow: Login → Get tasks → Create task → Update task → Mark complete → Delete task