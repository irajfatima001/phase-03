#!/usr/bin/env python3
"""
Database initialization script to create tables
"""

import asyncio
from sqlmodel import SQLModel
from src.database.session import engine
from src.models.user import User
from src.models.task import Task


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(SQLModel.metadata.create_all)


if __name__ == "__main__":
    asyncio.run(create_tables())
    print("Tables created successfully!")