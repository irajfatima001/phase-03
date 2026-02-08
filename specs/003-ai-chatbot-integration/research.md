# Research: AI-Powered Todo Chatbot Integration

## Overview
This document captures research findings for implementing the AI-powered todo chatbot integration with Cohere API and MCP tools.

## Decision: Cohere API Integration Approach
**Rationale**: The project requires using Cohere API for AI capabilities instead of OpenAI. We'll adapt the OpenAI Agents SDK to work with Cohere's API endpoints. Cohere offers strong language understanding capabilities that are suitable for interpreting natural language todo commands.

**Alternatives considered**:
- OpenAI API: Would require different API key and has different pricing structure
- Self-hosted LLM: Would add complexity for infrastructure and maintenance
- Anthropic Claude: Would require different integration approach

## Decision: MCP Tools Implementation
**Rationale**: Using the Official MCP SDK to expose task operations (add_task, list_tasks, complete_task, delete_task, update_task) allows the AI agent to call these functions directly when interpreting user commands. This creates a clean separation between AI interpretation and business logic.

**Alternatives considered**:
- Direct API calls from AI service: Would bypass MCP standards and create tight coupling
- Custom webhook system: Would reinvent existing MCP functionality

## Decision: Frontend Chatbot Component
**Rationale**: Integrating an OpenAI ChatKit-adapted component into the existing Next.js dashboard provides a familiar chat interface for users to interact with the AI. This maintains consistency with existing UI while adding new functionality.

**Alternatives considered**:
- Standalone chat interface: Would fragment user experience
- Voice-based interface: Would add complexity beyond current requirements

## Decision: Database Schema Extensions
**Rationale**: Adding Conversation and Message models to the existing Neon PostgreSQL database enables persistence of chat history while maintaining the stateless server architecture. This allows conversation context to be maintained across sessions.

**Alternatives considered**:
- Separate database: Would add complexity and potential consistency issues
- Client-side storage: Would not persist across devices/sessions

## Decision: Authentication and User Isolation
**Rationale**: Leveraging existing Better Auth JWT tokens ensures that all chatbot interactions respect user boundaries. The JWT token will be passed from frontend to backend to ensure all operations are scoped to the authenticated user.

**Alternatives considered**:
- Separate authentication for chatbot: Would complicate the security model
- Session-based approach: Would violate the stateless server requirement

## Technical Unknowns Resolved
- **Cohere API endpoints**: Confirmed compatibility with OpenAI-style function calling
- **MCP SDK integration**: Verified Official MCP SDK supports the required tool definitions
- **JWT token passing**: Confirmed Better Auth tokens can be passed to backend API calls
- **Stateless architecture**: Validated that conversation history can be stored in DB to maintain context