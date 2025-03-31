#!/bin/bash
echo "Starting server..."
echo "PORT: $PORT"
echo "Current directory: $(pwd)"
gunicorn --worker-class uvicorn.workers.UvicornWorker --bind "0.0.0.0:${PORT:-8000}" --log-level debug app:app 