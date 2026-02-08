#!/usr/bin/env python3
"""
Migration script to add status column to the tasks table.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlmodel import Session

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings


def add_status_column():
    """Add the status column to the tasks table."""
    print("Adding status column to tasks table...")
    
    # Create engine with async-compatible URL
    db_url = settings.get_database_url()
    engine = create_engine(db_url.replace("+asyncpg", ""))
    
    with Session(engine) as session:
        # Check if the column already exists
        result = session.exec(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'status'
        """)).fetchall()
        
        if result:
            print("Status column already exists.")
            return
        
        # Add the status column with a default value
        print("Adding status column...")
        session.exec(text("ALTER TABLE tasks ADD COLUMN status VARCHAR(50) DEFAULT 'pending'"))
        
        # Commit the transaction
        session.commit()
        print("Status column added successfully!")


if __name__ == "__main__":
    add_status_column()