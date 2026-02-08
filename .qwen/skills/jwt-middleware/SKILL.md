# Skill: jwt-middleware

**Name**: jwt-middleware  
**Description**: Generates FastAPI dependency to verify JWT from Better Auth, extract user_id, raise 401 if invalid

## Purpose
This skill generates a FastAPI dependency that verifies JWT tokens issued by Better Auth, extracts the user_id from the token, and raises a 401 error if the token is invalid. This ensures that only authenticated users can access protected endpoints and that each user can only access their own data.

## Allowed Tools
- code_write
- file_edit

## Implementation Instructions

### 1. Import Required Libraries
```python
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
import os
```

### 2. Define UserToken Model
```python
class UserToken(BaseModel):
    user_id: str
```

### 3. Configure JWT Settings
```python
# Get secret key from environment
SECRET_KEY = os.getenv("BETTER_AUTH_SECRET")
ALGORITHM = "HS256"
security = HTTPBearer()
```

### 4. Create JWT Verification Function
```python
def verify_token(token: str) -> Optional[dict]:
    """
    Verify JWT token and return payload if valid
    """
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        return payload
    except JWTError:
        return None
```

### 5. Create FastAPI Dependency
```python
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> UserToken:
    """
    FastAPI dependency to get current user from JWT token
    """
    token = credentials.credentials
    payload = verify_token(token)
    
    if payload is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    user_id: str = payload.get("sub")
    if user_id is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    return UserToken(user_id=user_id)
```

### 6. Usage in Endpoints
```python
from fastapi import Depends

@app.get("/api/tasks")
async def get_tasks(current_user: UserToken = Depends(get_current_user)):
    # Filter queries by current_user.user_id
    tasks = await get_tasks_by_user_id(current_user.user_id)
    return tasks
```

## Key Features
- Uses python-jose for JWT verification
- Retrieves SECRET_KEY from environment using os.getenv("BETTER_AUTH_SECRET")
- Uses HS256 algorithm for token decoding
- Extracts user_id from token["sub"] claim
- Raises HTTPException with 401 status if token is invalid
- Returns UserToken model containing the user_id
- Designed to work with FastAPI's dependency injection system
- Enables user isolation by filtering queries by user.user_id

## Security Considerations
- Never expose the BETTER_AUTH_SECRET in client-side code
- Ensure all protected endpoints use the get_current_user dependency
- Always filter database queries by the authenticated user's ID to prevent data leakage between users
- The middleware automatically handles token extraction from Authorization header