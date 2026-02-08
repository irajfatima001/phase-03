#!/usr/bin/env python3
"""
Test script for the AI Todo Chatbot API endpoints.
This script tests all the main API endpoints to ensure they're working properly.
"""

import requests
import json
import uuid
from datetime import datetime


BASE_URL = "http://127.0.0.1:8000"
HEADERS = {
    "Content-Type": "application/json"
}


def test_health_endpoint():
    """Test the health check endpoint."""
    print("Testing health endpoint...")
    try:
        response = requests.get(f"{BASE_URL}/health")
        print(f"Health check: {response.status_code} - {response.json()}")
        return True
    except Exception as e:
        print(f"Health check failed: {e}")
        return False


def test_register_and_login():
    """Test user registration and login."""
    print("\nTesting registration and login...")
    
    # Generate unique email for testing
    test_email = f"test_{uuid.uuid4()}@example.com"
    test_password = "password123"
    test_name = "Test User"
    
    # Register
    try:
        register_data = {
            "email": test_email,
            "password": test_password,
            "name": test_name
        }
        register_response = requests.post(f"{BASE_URL}/auth/register", 
                                         headers=HEADERS, 
                                         json=register_data)
        print(f"Register: {register_response.status_code}")
        
        if register_response.status_code == 200:
            token_data = register_response.json()
            access_token = token_data.get("access_token")
            
            # Add token to headers for subsequent requests
            auth_headers = HEADERS.copy()
            auth_headers["Authorization"] = f"Bearer {access_token}"
            
            # Test protected endpoint (get tasks)
            tasks_response = requests.get(f"{BASE_URL}/api/v1/tasks", 
                                         headers=auth_headers)
            print(f"Get tasks: {tasks_response.status_code}")
            
            # Create a test task
            task_data = {
                "title": "Test Task",
                "description": "This is a test task",
                "completed": False
            }
            create_task_response = requests.post(f"{BASE_URL}/api/v1/tasks", 
                                                headers=auth_headers, 
                                                json=task_data)
            print(f"Create task: {create_task_response.status_code}")
            
            if create_task_response.status_code == 200:
                task = create_task_response.json()
                task_id = task.get("id")
                
                # Get the created task
                get_task_response = requests.get(f"{BASE_URL}/api/v1/tasks/{task_id}", 
                                                headers=auth_headers)
                print(f"Get task: {get_task_response.status_code}")
                
                # Update the task
                update_data = {
                    "title": "Updated Test Task",
                    "completed": True
                }
                update_task_response = requests.patch(f"{BASE_URL}/api/v1/tasks/{task_id}", 
                                                     headers=auth_headers, 
                                                     json=update_data)
                print(f"Update task: {update_task_response.status_code}")
                
                # Toggle task completion
                complete_data = {"complete": False}
                complete_response = requests.put(f"{BASE_URL}/api/v1/tasks/{task_id}/complete", 
                                                headers=auth_headers, 
                                                json=complete_data)
                print(f"Toggle task completion: {complete_response.status_code}")
                
                # Delete the task
                delete_response = requests.delete(f"{BASE_URL}/api/v1/tasks/{task_id}", 
                                                 headers=auth_headers)
                print(f"Delete task: {delete_response.status_code}")
            
            # Test conversations
            # Create a conversation
            conversation_data = {"title": "Test Conversation"}
            create_conv_response = requests.post(f"{BASE_URL}/api/v1/conversations",
                                                headers=auth_headers,
                                                json=conversation_data)
            print(f"Create conversation: {create_conv_response.status_code}")

            if create_conv_response.status_code == 200:
                conv = create_conv_response.json()
                conv_id = conv.get("id")

                # Get conversations list
                get_convs_response = requests.get(f"{BASE_URL}/api/v1/conversations",
                                                 headers=auth_headers)
                print(f"Get conversations: {get_convs_response.status_code}")

                # Get specific conversation
                get_conv_response = requests.get(f"{BASE_URL}/api/v1/conversations/{conv_id}",
                                                headers=auth_headers)
                print(f"Get specific conversation: {get_conv_response.status_code}")

                # Add message to conversation
                message_data = {"content": "Hello, AI assistant!"}
                add_msg_response = requests.post(f"{BASE_URL}/api/v1/conversations/{conv_id}/messages",
                                                headers=auth_headers,
                                                json=message_data)
                print(f"Add message to conversation: {add_msg_response.status_code}")

            # Test initiate conversation
            initiate_data = {"content": "Can you help me manage my tasks?"}
            initiate_response = requests.post(f"{BASE_URL}/api/v1/conversations/initiate",
                                             headers=auth_headers,
                                             json=initiate_data)
            print(f"Initiate conversation: {initiate_response.status_code}")
            
            return True
    except Exception as e:
        print(f"Registration/login test failed: {e}")
        return False


def main():
    """Run all tests."""
    print("Starting API endpoint tests...\n")
    
    # Test health endpoint
    health_ok = test_health_endpoint()
    
    if health_ok:
        # Test registration, login, and other endpoints
        test_register_and_login()
    
    print("\nAPI endpoint tests completed.")


if __name__ == "__main__":
    main()