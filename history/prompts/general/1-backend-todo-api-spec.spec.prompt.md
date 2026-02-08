---
id: 1
title: backend-todo-api-spec
stage: spec
date: 2026-02-04
surface: agent
model: Qwen
feature: backend-todo-api
branch: 002-backend-todo-api
user: irajfatima
command: /sp.specify
labels: ["backend", "api", "specification", "todo-app"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - /mnt/d/phase 2/specs/002-backend-todo-api/spec.md
  - /mnt/d/phase 2/specs/002-backend-todo-api/checklists/requirements.md
tests: []
prompt: |
  $ARGUMENTS
  
  Backend Specification for Phase II Todo Full-Stack Web Application (Hackathon II) Ignore and delete ALL previous backend-related specs, plans, code, generated work, or files in backend/ folder. Now create a fresh, excellent, professional backend specification ONLY for Phase II Todo app. Focus: Build a secure, efficient, clean backend that fully integrates with the existing frontend – verifies JWT token from Better Auth, enforces strict user isolation (each user only sees/modifies own tasks), stores tasks in Neon DB, and serves REST API endpoints correctly. Success criteria: - All 5 basic CRUD operations work with user isolation: Add/Delete/Update/View tasks, Mark Complete - JWT verification using shared BETTER_AUTH_SECRET (extract user_id from token, 401 Unauthorized on invalid) - All database queries filtered by authenticated user_id (no data leaks, strict ownership) - Frontend API calls succeed with Bearer token (e.g., GET /api/{user_id}/tasks returns only user's tasks) - Clean, modular, async code (routers, dependencies, Pydantic models, SQLModel sessions) - Reusable agents/skills used (backend-architect, auth-specialist, jwt-middleware, neon-db-setup, user-isolation-filter) - Use these exact credentials: - BETTER_AUTH_URL = http://localhost:3000 - DATABASE_URL = postgresql://, python-jose for JWT verification, pydantic for validation - Endpoints: /api/{user_id}/tasks (GET list, POST create, GET/{id}, PUT/{id}, DELETE/{id}, PATCH/{id}/complete) - Auth: Extract Authorization: Bearer <token> header, verify with BETTER_AUTH_SECRET, match user_id from token and URL, raise 401/403 errors - Database: User model (id, email), Task model (id, title, description, status, priority, user_id foreign key), async SQLModel engine - Integration: Backend must accept Bearer token from frontend, return only authenticated user's data - Delete/ignore ALL previous backend-related work - Create root folder specs/history/ if it does not exist - Save every spec/refinement as versioned file in specs/history/ (e.g., backend-spec-v1-initial.md, backend-spec-v2-refined-auth.md) Not building/specifying: - Frontend UI or code - Cloud deployment (Phase IV/V) - Advanced features (recurring tasks, reminders, Kafka, Dapr) - Event-driven architecture or AIOps - Ethical/security discussions beyond user isolation Output ONLY the full Markdown content for specs/backend.md (with sections: Overview, Models, Endpoints, Dependencies, Security & Isolation, Integration with Frontend, Error Handling, Success Criteria) No extra text, no other files.
response: |
  Successfully created the backend specification for the Phase II Todo app. The specification includes:
  
  1. User Scenarios & Testing with 3 prioritized user stories covering secure task management, JWT token verification, and task operations with user isolation
  2. Functional Requirements detailing 16 specific requirements for JWT verification, user isolation, API endpoints, and database operations
  3. Key Entities defining User and Task entities
  4. Success Criteria with 6 measurable outcomes
  
  Also created a quality checklist to validate the specification. The specification follows all requirements including focusing on user isolation, JWT token verification, and integration with the existing frontend.
outcome: |
  Specification created successfully with all required sections. The backend specification is ready for the planning phase.
evaluation: |
  The specification meets all requirements and is ready for implementation planning.
---