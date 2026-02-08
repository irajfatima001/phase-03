#!/usr/bin/env python3
"""
Database update script for the AI Todo Chatbot application.
This script updates the database schema to include new fields.
"""

import sys
import os
from sqlmodel import SQLModel

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database.session import engine
from src.models import *  # Import all models to register them with SQLModel metadata


def update_tables():
    """Update database tables to include new fields."""
    print("Updating database tables...")
    
    # Drop and recreate all tables (for development purposes)
    SQLModel.metadata.drop_all(bind=engine)
    SQLModel.metadata.create_all(bind=engine)
    
    print("Database tables updated successfully!")


if __name__ == "__main__":
    update_tables()