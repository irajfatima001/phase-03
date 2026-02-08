#!/usr/bin/env python3
"""
Migration script to add priority column to the tasks table.
"""

import sys
import os
from sqlalchemy import create_engine, text
from sqlmodel import Session

# Add the src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.core.config import settings


def add_priority_column():
    """Add the priority column to the tasks table."""
    print("Adding priority column to tasks table...")
    
    # Create engine with async-compatible URL
    db_url = settings.get_database_url()
    engine = create_engine(db_url.replace("+asyncpg", ""))
    
    with Session(engine) as session:
        # Check if the column already exists
        result = session.exec(text("""
            SELECT column_name 
            FROM information_schema.columns 
            WHERE table_name = 'tasks' AND column_name = 'priority'
        """)).fetchall()
        
        if result:
            print("Priority column already exists.")
            return
        
        # Add the priority column with a default value
        print("Adding priority column...")
        session.exec(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR(20) DEFAULT 'medium'"))
        
        # Commit the transaction
        session.commit()
        print("Priority column added successfully!")


if __name__ == "__main__":
    add_priority_column()