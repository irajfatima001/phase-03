#!/usr/bin/env python3
"""
Debug script to test task endpoints and get detailed error information.
"""

import requests
import json


BASE_URL = "http://127.0.0.1:8000"
HEADERS = {
    "Content-Type": "application/json"
}


def test_task_endpoints():
    """Test task endpoints and get detailed error information."""
    print("Testing task endpoints...")
    
    # Step 1: Register a user
    import uuid
    print("\n1. Registering user...")
    unique_email = f"test_{uuid.uuid4()}@example.com"
    register_data = {
        "email": unique_email,
        "password": "password123",
        "name": "Test User"
    }
    register_response = requests.post(f"{BASE_URL}/auth/register", 
                                     headers=HEADERS, 
                                     json=register_data)
    print(f"Register: {register_response.status_code}")
    
    if register_response.status_code != 200:
        print(f"Register failed: {register_response.text}")
        return
    
    token_data = register_response.json()
    access_token = token_data.get("access_token")
    
    # Add token to headers
    auth_headers = HEADERS.copy()
    auth_headers["Authorization"] = f"Bearer {access_token}"
    
    # Step 2: Try to create a task
    print("\n2. Creating task...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test task",
        "completed": False,
        "priority": "medium"  # Add priority to match the updated model
    }
    create_response = requests.post(f"{BASE_URL}/api/v1/tasks", 
                                   headers=auth_headers, 
                                   json=task_data)
    print(f"Create task: {create_response.status_code}")
    if create_response.status_code != 200:
        print(f"Create task failed: {create_response.text}")
        print(f"Response headers: {dict(create_response.headers)}")
    
    # Step 3: Try to get tasks
    print("\n3. Getting tasks...")
    get_response = requests.get(f"{BASE_URL}/api/v1/tasks", 
                                headers=auth_headers)
    print(f"Get tasks: {get_response.status_code}")
    if get_response.status_code != 200:
        print(f"Get tasks failed: {get_response.text}")
        print(f"Response headers: {dict(get_response.headers)}")


if __name__ == "__main__":
    test_task_endpoints()