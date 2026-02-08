from datetime import datetime, timedelta
from typing import Optional
from jose import JWTError, jwt
from fastapi import HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from pydantic import BaseModel
from .config import settings
from .logging_config import get_logger
import uuid


logger = get_logger(__name__)


class TokenData(BaseModel):
    user_id: Optional[str] = None


security = HTTPBearer()


def verify_token(token: str) -> TokenData:
    """
    Verify the JWT token and return the user ID
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(
            token, settings.BETTER_AUTH_SECRET, algorithms=["HS256"]
        )
        user_id: str = payload.get("sub")
        if user_id is None:
            logger.warning("Token validation failed: no user_id in payload")
            raise credentials_exception
        token_data = TokenData(user_id=user_id)
    except JWTError as e:
        logger.error(f"Token validation failed: {str(e)}")
        raise credentials_exception
    except Exception as e:
        logger.error(f"Unexpected error during token validation: {str(e)}")
        raise credentials_exception
    return token_data


async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)) -> uuid.UUID:
    """
    Get the current user from the JWT token
    """
    try:
        token_data = verify_token(credentials.credentials)
        user_id = uuid.UUID(token_data.user_id)
        logger.info(f"Successfully authenticated user: {user_id}")
        return user_id
    except ValueError as e:
        logger.error(f"Invalid user ID format in token: {token_data.user_id if 'token_data' in locals() else 'unknown'}")
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user ID format in token"
        )
    except HTTPException:
        # Re-raise HTTP exceptions (like 401) as-is
        raise
    except Exception as e:
        logger.error(f"Unexpected error during user authentication: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Internal server error during authentication"
        )


def handle_unauthorized_access(request_info: str = ""):
    """
    Handle unauthorized access attempts with comprehensive logging
    """
    logger.warning(f"Unauthorized access attempt: {request_info}")
    raise HTTPException(
        status_code=status.HTTP_403_FORBIDDEN,
        detail="Access denied: Insufficient permissions"
    )


def handle_resource_not_found(resource_type: str, resource_id: str = ""):
    """
    Handle resource not found errors with appropriate logging
    """
    msg = f"{resource_type} not found"
    if resource_id:
        msg += f": {resource_id}"
    logger.info(msg)
    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=msg
    )