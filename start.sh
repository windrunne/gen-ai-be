#!/bin/bash
# Start script for backend

# Activate virtual environment if it exists
if [ -d "venv" ]; then
    source venv/bin/activate
fi

# Run the FastAPI server
uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --reload
