#!/usr/bin/env python3
"""
Test script to verify that the backend can start without errors
"""

import sys
import os

# Add the backend directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '.'))

try:
    # Try to import the main app
    from main import app
    print("✓ Successfully imported main app")
    
    # Try to import key components
    from src.api.v1.conversations import router as conversations_router
    print("✓ Successfully imported conversations router")
    
    from src.models.conversation import Conversation
    print("✓ Successfully imported Conversation model")
    
    from src.models.message import Message
    print("✓ Successfully imported Message model")
    
    from src.services.conversation_service import ConversationService
    print("✓ Successfully imported ConversationService")
    
    from src.api.deps import get_db_session, CurrentUser
    print("✓ Successfully imported dependencies")
    
    print("\n✓ All imports successful! The application should run without import errors.")
    print("\nTo run the application, use:")
    print("cd /mnt/d/phase 3/backend")
    print("./start.sh")
    print("\nor")
    print("uvicorn main:app --host 0.0.0.0 --port 8000 --reload")
    
except ImportError as e:
    print(f"✗ Import error: {e}")
    sys.exit(1)
except Exception as e:
    print(f"✗ Other error: {e}")
    sys.exit(1)