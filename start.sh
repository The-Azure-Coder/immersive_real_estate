#!/bin/bash

# Exit immediately if a command exits with a non-zero status
set -e

# Run database migrations
echo "Running database migrations..."
alembic upgrade head

# Start the application
echo "Starting FastAPI server..."
# Using uvicorn as recommended in the implementation plan
# Note: For production, we can switch this to Gunicorn + Uvicorn workers
exec uvicorn app.main:app --host 0.0.0.0 --port 8000
