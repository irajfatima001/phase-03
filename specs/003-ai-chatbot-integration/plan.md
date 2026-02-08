# Implementation Plan: AI-Powered Todo Chatbot Integration

**Branch**: `003-ai-chatbot-integration` | **Date**: 2026-02-07 | **Spec**: [/specs/003-ai-chatbot-integration/spec.md](file:///mnt/d/phase%203/specs/003-ai-chatbot-integration/spec.md)
**Input**: Feature specification from `/specs/003-ai-chatbot-integration/spec.md`

**Note**: This template is filled in by the `/sp.plan` command. See `.specify/templates/commands/plan.md` for the execution workflow.

## Summary

Integrate a conversational AI chatbot into the existing Phase II full-stack Todo app that manages todos through natural language (add, delete, update, mark complete, list tasks) using Cohere API key for AI capabilities, adapting OpenAI SDK code to use Cohere API for agent logic and tool calling, exposing task operations via MCP tools, and ensuring full user isolation and seamless integration with existing backend API endpoints.

## Technical Context

**Language/Version**: Python 3.11, JavaScript/TypeScript, Next.js 14+
**Primary Dependencies**: FastAPI, Cohere API, Official MCP SDK, Better Auth, SQLModel, Neon PostgreSQL
**Storage**: Neon PostgreSQL database with extended Conversation and Message models
**Testing**: pytest for backend, Jest/React Testing Library for frontend
**Target Platform**: Web application (Next.js frontend + FastAPI backend)
**Project Type**: Web application with frontend and backend components
**Performance Goals**: <5s response time for chatbot interactions, 95% uptime
**Constraints**: User isolation via JWT, stateless server architecture, secure API communication
**Scale/Scope**: Individual user task management with conversation history

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

- ✅ Strict Spec-Driven Development: Following detailed specification from spec.md
- ✅ Reusable Intelligence Architecture: Using frontend-ui, backend-architect, auth-specialist, security-isolator, spec-validator agents
- ✅ Full Integration with Existing System: Chatbot will call existing /api/{user_id}/tasks... endpoints with Bearer token
- ✅ Absolute User Isolation & Security: All operations filtered by authenticated user_id from JWT
- ✅ Stateless Server Architecture: Conversation state persisted in Neon DB
- ✅ Cohere API Integration: Using Cohere API key for all AI operations
- ✅ MCP Tools Standard: Exposing task operations via Official MCP SDK
- ✅ Clean, Modular, Secure Code Standards: Following async operations, Pydantic validation
- ✅ Frontend Excellence: Building Next.js 14+ App Router interface with chatbot component
- ✅ Backend Integrity: Extending existing FastAPI with MCP server
- ✅ Database Persistence: Extending Neon PostgreSQL with Conversation and Message models
- ✅ Authentication Compliance: Using Better Auth JWT from frontend session

## Project Structure

### Documentation (this feature)

```text
specs/003-ai-chatbot-integration/
├── plan.md              # This file (/sp.plan command output)
├── research.md          # Phase 0 output (/sp.plan command)
├── data-model.md        # Phase 1 output (/sp.plan command)
├── quickstart.md        # Phase 1 output (/sp.plan command)
├── contracts/           # Phase 1 output (/sp.plan command)
└── tasks.md             # Phase 2 output (/sp.tasks command - NOT created by /sp.plan)
```

### Source Code (repository root)

```text
backend/
├── src/
│   ├── models/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── task.py
│   │   ├── conversation.py          # New: Conversation model
│   │   └── message.py               # New: Message model
│   ├── services/
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── conversation_service.py  # New: Conversation management
│   │   └── cohere_service.py        # New: Cohere API integration
│   ├── api/
│   │   ├── __init__.py
│   │   ├── deps.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── tasks.py
│   │   │   └── conversations.py     # New: Conversation endpoints
│   │   └── mcp/                     # New: MCP server
│   │       ├── __init__.py
│   │       ├── server.py
│   │       └── tools.py             # New: MCP tools for task operations
│   ├── core/
│   │   ├── __init__.py
│   │   ├── config.py
│   │   └── security.py
│   └── main.py
└── tests/
    ├── unit/
    ├── integration/
    └── contract/

frontend/
├── src/
│   ├── components/
│   │   ├── ui/
│   │   ├── chatbot/                 # New: Chatbot UI component
│   │   │   ├── Chatbot.tsx
│   │   │   ├── ChatMessage.tsx
│   │   │   └── ChatInput.tsx
│   │   └── dashboard/
│   ├── pages/
│   │   ├── index.tsx
│   │   └── dashboard/
│   ├── lib/
│   │   ├── auth.ts
│   │   └── api.ts
│   └── hooks/
└── tests/
    ├── unit/
    └── integration/
```

**Structure Decision**: Web application structure selected with separate frontend and backend components. Backend extends existing FastAPI with new models, services, and MCP server. Frontend adds new chatbot UI component to existing dashboard.

## Complexity Tracking

> **Fill ONLY if Constitution Check has violations that must be justified**

| Violation | Why Needed | Simpler Alternative Rejected Because |
|-----------|------------|-------------------------------------|
| [None identified] | [N/A] | [N/A] |