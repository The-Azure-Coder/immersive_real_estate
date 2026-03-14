#!/bin/bash
# Exit immediately if a command exits with a non-zero status.
set -e

# Wait for the database to be ready
echo "Waiting for database to be ready..."
# The DATABASE_URL is available from the Render environment
until pg_isready -h $(echo $DATABASE_URL | awk -F'[@/:]' '{print $6}') -p $(echo $DATABASE_URL | awk -F'[@/:]' '{print $7}') -U $(echo $DATABASE_URL | awk -F'[@/:]' '{print $4}'); do
  echo "Database is not ready yet. Waiting..."
  sleep 3
done
echo "Database is ready."

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
