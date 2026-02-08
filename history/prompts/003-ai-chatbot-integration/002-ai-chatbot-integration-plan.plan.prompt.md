---
id: 002
title: Ai Chatbot Integration Plan
stage: plan
date: 2026-02-07
surface: agent
model: Qwen Code
feature: 003-ai-chatbot-integration
branch: 003-ai-chatbot-integration
user: irajfatima
command: /sp.plan Phase III AI-Powered Todo Chatbot Integration Plan
labels: [planning, ai-chatbot, mcp-tools, database-models]
links:
  spec: /mnt/d/phase 3/specs/003-ai-chatbot-integration/spec.md
  ticket: null
  adr: null
  pr: null
files:
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/plan.md
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/research.md
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/data-model.md
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/quickstart.md
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/contracts/conversation-api-contract.md
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/contracts/mcp-tools-contract.md
tests:
 - /mnt/d/phase 3/specs/003-ai-chatbot-integration/plan.md
---

## Prompt

Phase III AI-Powered Todo Chatbot Integration Plan (Hackathon II)

Reference documents: Constitution.md + specs/phase3-chatbot.md (AI chatbot integrated into Phase II full-stack Todo app using Cohere API key, OpenAI Agents SDK adapted to Cohere, Official MCP SDK, MCP tools for task operations, stateless server, DB-persisted conversation state)


Focus: Create a clear, step-by-step development plan to integrate a conversational AI chatbot into the existing Phase II full-stack Todo app that manages todos through natural language (add, delete, update, mark complete, list tasks) using Cohere API key for AI capabilities, adapting OpenAI SDK code to use Cohere API for agent logic and tool calling, exposing task operations via MCP tools, and ensuring full user isolation and seamless integration with existing backend API endpoints.

Success criteria:
- Chatbot handles all 5 basic features via natural language (add, delete, update, mark complete, list tasks)
- Full functionality: User-specific data only (via JWT user_id), confirms actions, handles errors gracefully
- Integration perfect: Chatbot frontend component embeds in existing Phase II dashboard, backend MCP tools call existing /api/{user_id}/tasks... endpoints with Bearer token
- Conversation context maintained: Persists history in Neon DB, stateless server
- Cohere API adapted successfully: Use Cohere API key  modify OpenAI Agents SDK code to use Cohere API endpoints
- MCP tools exposed: add_task, list_tasks, complete_task, delete_task, update_task via Official MCP SDK
- Reusable agents/skills used (frontend-ui, backend-architect, auth-specialist, security-isolator, spec-validator)

Constraints:
- Technology: OpenAI ChatKit (adapted for Cohere), OpenAI Agents SDK (adapted to Cohere API), Official MCP SDK, Cohere API key for AI, FastAPI for MCP server, SQLModel for DB
- Frontend: Next.js 14+ App Router, embed chatbot UI component
- Backend: Extend existing FastAPI backend with MCP server for tool exposure
- Database: Extend existing Neon PostgreSQL with Conversation and Message models
- Authentication: Better Auth JWT from frontend session, passed to backend API calls
- Stateless server: Persist conversation history in Neon DB
- Save every plan/refinement as versioned file in specs/history/ (e.g., phase3-plan-v1-initial.md, phase3-plan-v2-tool-calling.md)

Not building/specifying:
- Full frontend redesign (only chatbot UI component integration)
- Advanced features (voice input, recurring tasks – save for bonus)
- Cloud deployment (Phase IV/V)
- Ethical/security discussions beyond user isolation

Output ONLY the full Markdown content for specs/plans/phase3-chatbot-plan.md
Include:
1. Overview (high-level goal + Phase II integration)
2. Numbered step-by-step plan (12–16 steps)
3. Breakdown into small, independent tasks (assignable to frontend-ui and backend-architect sub-agents)
4. How to use frontend-ui, backend-architect, auth-specialist, security-isolator, spec-validator sub-agents and nextjs-component, jwt-middleware, fastapi-crud, neon-db-setup, user-isolation-filter skills
5. Success criteria per step (e.g., "Chatbot adds task via MCP tool", "Conversation history persisted in DB")
6. Integration checkpoints (how to test chatbot with existing frontend/backend after each major step)

No extra text, no other files.

## Response snapshot

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

## Outcome

- ✅ Impact: Created comprehensive implementation plan for AI chatbot integration
- 🧪 Tests: Plan validated against constitution principles with all gates passed
- 📁 Files: Created plan.md, research.md, data-model.md, quickstart.md, and contract definitions
- 🔁 Next prompts: Ready to proceed with task breakdown phase
- 🧠 Reflection: Plan addresses all requirements while maintaining integration with existing system

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): PASS - All constitution gates passed
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Begin task breakdown based on this plan