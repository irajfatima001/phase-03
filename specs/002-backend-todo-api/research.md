# Research: Phase II Todo Backend

## Decision: Technology Stack Selection
**Rationale**: Selected FastAPI, SQLModel, and python-jose based on requirements and best practices for building secure, async Python APIs with PostgreSQL integration.

**Alternatives considered**:
- Flask vs FastAPI: Chose FastAPI for built-in async support, automatic API documentation, and Pydantic integration.
- SQLAlchemy vs SQLModel: Chose SQLModel for better Pydantic compatibility and cleaner syntax.
- PyJWT vs python-jose: Chose python-jose for better async support and JWK handling.

## Decision: JWT Verification Implementation
**Rationale**: Using python-jose with the provided BETTER_AUTH_SECRET (jCFvRhqz7MEOLoNE53UWVUIadbgv5lQH) to verify JWT tokens from Better Auth, extracting user_id from the payload to enforce user isolation.

**Alternatives considered**:
- Custom auth vs standard JWT: Chose standard JWT for interoperability with Better Auth.
- Different verification libraries: python-jose chosen for async support and security features.

## Decision: Database Connection Strategy


**Alternatives considered**:
- Different ORMs: SQLModel chosen for Pydantic compatibility.
- Different DB engines: Neon PostgreSQL chosen as per requirements.

## Decision: API Endpoint Design
**Rationale**: Following REST conventions with /api/{user_id}/tasks endpoints to enforce user isolation at the URL level, matching user_id from JWT token with URL parameter.

**Alternatives considered**:
- Different URL structures: Kept user_id in URL path to make user isolation explicit in the API design.
- Header-based user identification: URL parameter chosen for clarity and consistency.