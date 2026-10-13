#!/usr/bin/env bash
# exit on error
set -o errexit

# Always run from this script's directory (repo root has no
# requirements.txt/manage.py; Render's buildCommand runs from repo root).
cd "$(dirname "$0")"

echo "Installing Python dependencies..."
pip install -r requirements.txt

echo "Building React frontend..."
if command -v npm >/dev/null 2>&1; then
  (cd frontend && npm install && npm run build)
else
  echo "Warning: npm not found, skipping frontend build (homepage will show API status)"
fi

echo "Collecting static files..."
python manage.py collectstatic --no-input

echo "Running database migrations..."
python manage.py migrate

echo "Populating initial data..."
python manage.py populate_data || echo "Warning: Could not populate data (may already exist)"

echo "Build completed successfully!"
