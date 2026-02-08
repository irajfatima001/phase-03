#!/bin/bash
# Startup script for the AI Todo Chatbot Frontend

# Exit on any error
set -e

echo "Starting AI Todo Chatbot Frontend..."

# Install dependencies
npm install

# Start the Next.js development server
npm run dev