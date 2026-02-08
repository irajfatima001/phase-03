#!/usr/bin/env python3
"""
Database initialization script for the AI Todo Chatbot application.
This script creates all necessary tables in the database.
"""

import sys
import os
from sqlmodel import SQLModel

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.session import engine
from src.models import *  # Import all models to register them with SQLModel metadata


def create_tables():
    """Create all tables in the database."""
    print("Creating database tables...")
    
    # Create all tables
    SQLModel.metadata.create_all(bind=engine)
    
    print("Database tables created successfully!")


if __name__ == "__main__":
    create_tables()