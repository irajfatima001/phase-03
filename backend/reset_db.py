#!/usr/bin/env python3
"""
Database reset script for the AI Todo Chatbot application.
This script drops and recreates all database tables to align with the updated models.
"""

import sys
import os
from sqlmodel import SQLModel, create_engine
from sqlalchemy import text

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings
from src.models import *  # Import all models to register them with SQLModel metadata


def reset_database():
    """Reset the database by dropping and recreating all tables."""
    print("Resetting database...")
    
    # Create engine with async-compatible URL
    db_url = settings.get_database_url()
    engine = create_engine(db_url.replace("+asyncpg", ""))
    
    # Drop all tables first
    print("Dropping all tables...")
    SQLModel.metadata.drop_all(bind=engine)
    
    # Create all tables
    print("Creating all tables...")
    SQLModel.metadata.create_all(bind=engine)
    
    print("Database reset successfully!")


if __name__ == "__main__":
    reset_database()