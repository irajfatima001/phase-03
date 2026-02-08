#!/usr/bin/env python3
"""
Database cleanup script for the AI Todo Chatbot application.
This script handles the specific PostgreSQL enum type issue.
"""

import sys
import os
from sqlalchemy import create_engine, text

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings


def cleanup_database():
    """Clean up the database by dropping tables and enum types."""
    print("Cleaning up database...")
    
    # Create engine with async-compatible URL
    db_url = settings.get_database_url()
    engine = create_engine(db_url.replace("+asyncpg", ""))
    
    with engine.connect() as conn:
        # First, drop all tables
        print("Dropping all tables...")
        conn.execute(text("DROP SCHEMA IF EXISTS public CASCADE"))
        conn.execute(text("CREATE SCHEMA public"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO postgres"))
        conn.execute(text("GRANT ALL ON SCHEMA public TO public"))
        conn.commit()
    
    print("Database cleaned up successfully!")


if __name__ == "__main__":
    cleanup_database()