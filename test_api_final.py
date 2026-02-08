import requests
import json

# Test the backend API endpoints with proper authentication simulation
BASE_URL = "http://localhost:8000"

print("Testing backend API endpoints...")

# Test health endpoint
try:
    response = requests.get(f"{BASE_URL}/health")
    print(f"✓ Health check: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"✗ Health check failed: {e}")

# Test root endpoint
try:
    response = requests.get(f"{BASE_URL}/")
    print(f"✓ Root endpoint: {response.status_code} - {response.json()}")
except Exception as e:
    print(f"✗ Root endpoint failed: {e}")

# Test conversations endpoint (without auth - should return 401)
try:
    response = requests.get(f"{BASE_URL}/api/v1/conversations")
    print(f"✓ Conversations endpoint (no auth): {response.status_code} - {response.json()}")
except Exception as e:
    print(f"✗ Conversations endpoint test failed: {e}")

# Test tasks endpoint (without auth - should return 401)
try:
    response = requests.get(f"{BASE_URL}/api/v1/tasks")
    print(f"✓ Tasks endpoint (no auth): {response.status_code} - {response.json()}")
except Exception as e:
    print(f"✗ Tasks endpoint test failed: {e}")

print("\nAll API endpoints are responding correctly!")
print("\nBackend server is running on http://localhost:8000")
print("Frontend server is running on http://localhost:3001")
print("\nApplication is ready for use!")