#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Run database migrations with a check
echo "Running database migrations..."
if ! alembic upgrade head; then
    echo "Migration failed. Exiting."
    exit 1
fi
echo "Migrations completed successfully."

# Start the application with Gunicorn
echo "Starting Gunicorn server..."
exec gunicorn -k uvicorn.workers.UvicornWorker -w 4 -b 0.0.0.0:8000 app.main:app
