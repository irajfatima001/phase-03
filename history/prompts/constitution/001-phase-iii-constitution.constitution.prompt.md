---
id: 001
title: Phase III Constitution
stage: constitution
date: 2026-02-07
surface: agent
model: Qwen Code
feature: phase-iii-ai-todo-chatbot
branch: main
user: irajfatima
command: /sp.constitution Phase III AI-Powered Todo Chatbot Integration
labels: [constitution, spec-driven-development, ai-integration]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - /mnt/d/phase 3/.specify/memory/constitution.md
tests:
 - /mnt/d/phase 3/.specify/memory/constitution.md
---

## Prompt

/sp.constitution Phase III AI-Powered Todo Chatbot Integration (Hackathon II: Spec-Driven Development)

Now create a fresh, professional, excellent Constitution.md ONLY for Phase III: AI-Powered Todo Chatbot integrated into existing Phase II full-stack Todo application.

Project: Integrate a conversational AI chatbot into the Phase II full-stack Todo app that manages todos through natural language (add, delete, update, mark complete, list tasks) using existing backend API endpoints, with full user isolation, using Cohere API key for AI capabilities, and adapting OpenAI SDK code to work via Cohere API for agent logic and tool calling.

Core principles:
- Strict spec-driven workflow: No manual coding, refine specs until perfect output from Qwen Code CLI
- Reusable intelligence: Mandatory use of sub-agents and skills for all code generation
- Full integration with Phase II: Chatbot calls existing FastAPI endpoints /api/{user_id}/tasks... with Bearer token from Better Auth, enforces user isolation
- User isolation & security: Every operation filtered by authenticated user_id from JWT, no data leaks, 401/403 errors
- Stateless server architecture: Persist conversation state in Neon DB (Conversation & Message models), server holds no state
- Cohere API usage: Use Cohere API key for all AI operations, adapt any OpenAI SDK code to use Cohere's equivalent endpoints for agent runner and tool calling
- MCP tools: Expose task operations (add_task, list_tasks, complete_task, delete_task, update_task) via Official MCP SDK
- Clean, modular, secure code: Async operations, Pydantic validation, error handling, no vulnerabilities

Key standards:
- Frontend: Next.js 14+ App Router, integrate chatbot UI component (OpenAI ChatKit adapted for Cohere)
- Backend: Extend existing FastAPI with MCP server using Official MCP SDK for tool exposure
- AI Framework: Adapt OpenAI Agents SDK to use Cohere API key for agent logic and tool calling
- Database: Extend existing Neon PostgreSQL with Conversation (user_id, id, created_at, updated_at) and Message (user_id, id, conversation_id, role, content, created_at) models
- Authentication: Better Auth JWT from frontend session, passed to backend API calls
- Specs history: All iterations and versions saved in specs/history/ folder with versioned files (e.g., phase3-chatbot-v1-initial.md)
- Reusable sub-agents: frontend-ui, backend-architect, auth-specialist, security-isolator, spec-validator
- Reusable skills: jwt-middleware, fastapi-crud, neon-db-setup, nextjs-component, user-isolation-filter

Constraints:
- No manual coding: All code generated via Qwen Code CLI
- Cohere API: Use Cohere API key for all AI operations, adapt OpenAI SDK code to Cohere's API
- Integration: Chatbot frontend component embeds in existing Phase II dashboard, backend MCP tools call existing Phase II API endpoints with JWT
- Stateless server: Persist conversation history in Neon DB, server ready for horizontal scaling
- Environment variables: Use BETTER_AUTH_SECRET for JWT, DATABASE_URL for Neon, COHERE_API_KEY for Cohere
- Testing: Local and production testing with user isolation enforced

Success criteria:
- Chatbot handles all 5 basic features via natural language (add, delete, update, mark complete, list tasks)
- Full functionality: User-specific data only, confirms actions, handles errors gracefully
- Integration perfect: Uses existing backend API with JWT, shows only logged-in user's tasks
- Conversation context maintained: Resumes from DB, remembers previous messages
- Cohere API adapted successfully: OpenAI SDK code modified to use Cohere for agent/tool calling
- All claims verified against specs, zero errors in integration
- Passes fact-checking review for security, isolation, and stateless architecture

Output ONLY the full raw Markdown content for Constitution.md.
Start with # Phase III Constitution
Include 10–12 clear, numbered articles/principles (strong, non-negotiable rules) covering all above points.
No extra text, no explanations, no mention of other phases or tools outside Qwen Code CLI.
Just the Markdown file content ready to save.

## Response snapshot

# Phase III Constitution

## Core Principles

### I. Strict Spec-Driven Development
All development follows a spec-driven workflow with no manual coding. Specifications must be refined until perfect output is achieved from Qwen Code CLI. No implementation proceeds without complete, validated specs.

### II. Reusable Intelligence Architecture
Mandatory use of sub-agents and skills for all code generation. Leverage specialized agents (frontend-ui, backend-architect, auth-specialist, security-isolator, spec-validator) and reusable skills (jwt-middleware, fastapi-crud, neon-db-setup, nextjs-component, user-isolation-filter) for all implementations.

### III. Full Integration with Existing System
Complete integration with Phase II full-stack Todo application. Chatbot must call existing FastAPI endpoints at /api/{user_id}/tasks... with Bearer token from Better Auth. Maintain backward compatibility and leverage existing infrastructure.

### IV. Absolute User Isolation & Security
Every operation must be filtered by authenticated user_id from JWT token. No data leaks between users are acceptable. Enforce 401/403 errors appropriately. Security vulnerabilities are non-negotiable.

### V. Stateless Server Architecture
Maintain stateless server design with conversation state persisted in Neon DB using Conversation and Message models. Server must be ready for horizontal scaling without holding any session state in memory.

### VI. Cohere API Integration
Use Cohere API key for all AI operations. Adapt any OpenAI SDK code to work with Cohere's equivalent endpoints for agent runner and tool calling. Ensure seamless AI functionality through Cohere's services.

### VII. MCP Tools Standard
Expose task operations (add_task, list_tasks, complete_task, delete_task, update_task) via Official MCP SDK. All tool integrations must follow MCP standards for interoperability and consistency.

### VIII. Clean, Modular, Secure Code Standards
Implement async operations, Pydantic validation, comprehensive error handling, and eliminate all vulnerabilities. Code must be clean, maintainable, and follow security best practices throughout the codebase.

### IX. Frontend Excellence
Build Next.js 14+ App Router interface with integrated chatbot UI component. Adapt OpenAI ChatKit for Cohere compatibility. Ensure responsive, intuitive user experience that seamlessly integrates with existing dashboard.

### X. Backend Integrity
Extend existing FastAPI with MCP server using Official MCP SDK for tool exposure. Maintain consistent API design patterns, error handling, and authentication flows across all endpoints.

### XI. Database Persistence
Extend existing Neon PostgreSQL schema with Conversation (user_id, id, created_at, updated_at) and Message (user_id, id, conversation_id, role, content, created_at) models. Ensure data integrity and proper indexing.

### XII. Authentication Compliance
Integrate Better Auth JWT from frontend session, passing to backend API calls securely. Maintain consistent authentication patterns across all components and enforce proper token validation.

## Development Standards

Technology Stack: Next.js 14+, FastAPI, Neon PostgreSQL, Better Auth, Cohere API, Official MCP SDK
Environment Variables: BETTER_AUTH_SECRET for JWT, DATABASE_URL for Neon, COHERE_API_KEY for Cohere
Testing: Comprehensive local and production testing with user isolation enforced
Specs History: All iterations saved in specs/history/ folder with versioned files

## Development Workflow

All code generation via Qwen Code CLI with sub-agent utilization. No manual coding permitted. Specs must be validated before implementation. Continuous integration with automated testing and security scanning.

## Governance

This constitution supersedes all other development practices. Amendments require formal documentation, approval, and migration planning. All pull requests and reviews must verify compliance with these principles. Complexity must be justified with clear benefits.

**Version**: 1.0.0 | **Ratified**: 2026-02-07 | **Last Amended**: 2026-02-07

## Outcome

- ✅ Impact: Created comprehensive constitution for Phase III AI-Powered Todo Chatbot Integration
- 🧪 Tests: Constitution file validated for completeness and adherence to requirements
- 📁 Files: /mnt/d/phase 3/.specify/memory/constitution.md created with all required principles
- 🔁 Next prompts: Ready to proceed with Phase III specification and implementation
- 🧠 Reflection: Constitution establishes strong foundation for spec-driven development approach with focus on security, integration, and AI capabilities

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All required principles included
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin Phase III specification based on constitution