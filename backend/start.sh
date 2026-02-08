#!/bin/bash
# Startup script for the AI Todo Chatbot Backend

# Exit on any error
set -e

echo "Starting AI Todo Chatbot Backend..."

# Install dependencies
pip install -r requirements.txt

# Run database migrations (if any)
# python -m alembic upgrade head

# Start the FastAPI application
uvicorn main:app --host 0.0.0.0 --port 8000 --reload