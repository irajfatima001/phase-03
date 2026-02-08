from sqlmodel import select
from src.models.user import User, UserCreate
from src.database.session import engine
from sqlmodel.ext.asyncio.session import AsyncSession
from typing import Optional
import uuid


async def get_user_by_email(email: str) -> Optional[User]:
    """
    Retrieve a user by email
    """
    async with AsyncSession(engine) as session:
        statement = select(User).where(User.email == email)
        result = await session.execute(statement)
        user = result.first()
        return user


async def create_user(user_data: UserCreate) -> User:
    """
    Create a new user
    """
    async with AsyncSession(engine) as session:
        user = User(
            id=str(uuid.uuid4()),
            email=user_data.email
        )
        session.add(user)
        await session.commit()
        await session.refresh(user)
        return user