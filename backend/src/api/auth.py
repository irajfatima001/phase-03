from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from datetime import timedelta, datetime
import uuid
from jose import jwt
from sqlmodel import Session, select
from src.models.user import User, UserCreate
from src.database.session import engine
from src.api.deps import get_db_session
from fastapi import Depends
from src.core.config import settings


ALGORITHM = "HS256"


def create_access_token(data: dict, expires_delta: timedelta = None):
    """
    Create a new JWT access token
    """
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=30)

    to_encode.update({"exp": expire})

    encoded_jwt = jwt.encode(to_encode, settings.BETTER_AUTH_SECRET, algorithm=ALGORITHM)
    return encoded_jwt


router = APIRouter()


class Token(BaseModel):
    access_token: str
    token_type: str


class LoginRequest(BaseModel):
    email: str
    password: str


class RegisterRequest(BaseModel):
    email: str
    password: str
    name: str


@router.post("/login", response_model=Token)
async def login(request: LoginRequest, db_session: Session = Depends(get_db_session)):
    """
    Authenticate user and return JWT token
    """
    try:
        # Find user by email
        statement = select(User).where(User.email == request.email)
        user = db_session.exec(statement).first()

        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Incorrect email or password"
            )

        # In a real app, you would verify the password here
        # For now, we'll just return a token

        access_token = create_access_token(
            data={"sub": str(user.id), "email": request.email},
            expires_delta=timedelta(minutes=30)
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication failed: {str(e)}"
        )


@router.post("/register", response_model=Token)
async def register(request: RegisterRequest, db_session: Session = Depends(get_db_session)):
    """
    Register a new user and return JWT token
    """
    try:
        # Check if user already exists
        statement = select(User).where(User.email == request.email)
        existing_user = db_session.exec(statement).first()

        if existing_user:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already registered"
            )

        # Create new user
        user_id = uuid.uuid4()
        user = User(
            id=user_id,
            email=request.email,
            name=request.name
        )

        db_session.add(user)
        db_session.commit()
        db_session.refresh(user)

        access_token = create_access_token(
            data={"sub": str(user.id), "email": request.email},
            expires_delta=timedelta(minutes=30)
        )

        return {"access_token": access_token, "token_type": "bearer"}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Registration failed: {str(e)}"
        )